#!/usr/bin/env python3
"""Exploratory CTC neck screen; test data is never loaded."""
import argparse, csv, hashlib, json, math, os, random, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[2]
WD = Path('/media/gmo/linhnx/workspace/workdir_Research')
DATA = WD / 'data/Indomain_curated/crops'
CACHE = WD / 'source/EditCTC/experiments/PAE_CTC/pilot_007/cache'
SPECS = {
 'N02': {'name':'Depthwise-CNN+height-attention-pool+Conv1D3+CTC', 'width_stride':4},
 'N04': {'name':'Depthwise-CNN+multiscale-Conv1D3-5+CTC', 'width_stride':4},
 'N07': {'name':'RGB-CNN+Sobel-edge-branch-concat+Conv1D3+CTC', 'width_stride':4},
}
CHARS = '0123456789'
MEAN=np.array([.485,.456,.406],np.float32); STD=np.array([.229,.224,.225],np.float32)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def readj(p): return json.loads(Path(p).read_text(encoding='utf8'))
def ids(p): return [Path(json.loads(x)['sample_id']).name for x in Path(p).read_text(encoding='utf8').splitlines() if x.strip()]
def save(p,x):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def jsonl(p,rows): Path(p).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf8')
def edit_ops(a,b):
 d=[[0]*(len(b)+1) for _ in range(len(a)+1)]
 for i in range(len(a)+1): d[i][0]=i
 for j in range(len(b)+1): d[0][j]=j
 for i,x in enumerate(a,1):
  for j,y in enumerate(b,1): d[i][j]=min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(x!=y))
 # deterministic backtrace, preferring substitution, then deletion, then insertion
 i,j=len(a),len(b); sub=dele=ins=0
 while i or j:
  if i and j and d[i][j]==d[i-1][j-1]+(a[i-1]!=b[j-1]):
   sub += a[i-1]!=b[j-1]; i-=1; j-=1
  elif i and d[i][j]==d[i-1][j]+1: dele+=1; i-=1
  else: ins+=1; j-=1
 return d[-1][-1],sub,dele,ins
def metrics(rows):
 n=len(rows); chars=sum(len(r['truth']) for r in rows); edits=sub=dele=ins=exact=wrong_same=0
 for r in rows:
  e,s,d,i=edit_ops(r['truth'],r['prediction']); edits+=e; sub+=s; dele+=d; ins+=i
  exact+=r['truth']==r['prediction']; wrong_same+=(r['truth']!=r['prediction'] and len(r['truth'])==len(r['prediction']))
 return {'n':n,'exact':exact,'exact_match':exact/max(1,n),'cer':edits/max(1,chars),'edit_chars':edits,'reference_chars':chars,'same_length_error_rate':wrong_same/max(1,n),'substitutions':sub,'deletions':dele,'insertions':ins}

class Crops(Dataset):
 def __init__(self,names,labels,image_paths): self.names=names; self.labels=labels; self.image_paths=image_paths
 def __len__(self): return len(self.names)
 def __getitem__(self,i):
  name=self.names[i]; text=self.labels[name]
  with Image.open(self.image_paths[name]) as im:
   im=im.convert('RGB'); w,h=im.size; nw=max(1,min(192,round(w*32/h)))
   a=np.asarray(im.resize((nw,32),Image.Resampling.BILINEAR),dtype=np.float32)/255
  x=np.empty((32,192,3),np.float32); x[:]=MEAN; x[:,:nw]=a
  x=torch.from_numpy(((x-MEAN)/STD).transpose(2,0,1).copy())
  y=torch.tensor([int(c)+1 for c in text],dtype=torch.long)
  return x,y,name,text,nw
def collate(batch):
 xs,ys,names,texts,widths=zip(*batch)
 return torch.stack(xs),torch.cat(ys),torch.tensor([len(y) for y in ys]),list(names),list(texts),torch.tensor(widths)

class DSBlock(nn.Module):
 def __init__(self,ci,co,stride=(1,1)):
  super().__init__(); self.net=nn.Sequential(nn.Conv2d(ci,ci,3,stride=stride,padding=1,groups=ci,bias=False),nn.BatchNorm2d(ci),nn.SiLU(),nn.Conv2d(ci,co,1,bias=False),nn.BatchNorm2d(co),nn.SiLU())
 def forward(self,x): return self.net(x)
class StandardBlock(nn.Module):
 def __init__(self,ci,co,stride=(1,1)):
  super().__init__(); self.net=nn.Sequential(nn.Conv2d(ci,co,3,stride=stride,padding=1,bias=False),nn.BatchNorm2d(co),nn.SiLU())
 def forward(self,x): return self.net(x)
class Network(nn.Module):
 def __init__(self,exp):
  super().__init__(); self.exp=exp
  self.cnn=nn.Sequential(DSBlock(3,32,(2,2)),DSBlock(32,64,(2,2)),DSBlock(64,96,(2,1)),DSBlock(96,128,(2,1)),DSBlock(128,128,(2,1)))
  if exp=='N02':
   self.height_score=nn.Conv2d(128,1,1); self.temporal=nn.Conv1d(128,128,3,padding=1)
  elif exp=='N04':
   self.temporal3=nn.Conv1d(128,128,3,padding=1); self.temporal5=nn.Conv1d(128,128,5,padding=2)
  elif exp=='N07':
   self.edge_cnn=nn.Sequential(DSBlock(1,16,(2,2)),DSBlock(16,32,(2,2)),DSBlock(32,32,(2,1)),DSBlock(32,32,(2,1)),DSBlock(32,32,(2,1)))
   self.temporal_projection=nn.Conv1d(160,128,1); self.temporal=nn.Conv1d(128,128,3,padding=1)
   self.register_buffer('sobel_x',torch.tensor([[-1.,0.,1.],[-2.,0.,2.],[-1.,0.,1.]]).view(1,1,3,3))
   self.register_buffer('sobel_y',torch.tensor([[-1.,-2.,-1.],[0.,0.,0.],[1.,2.,1.]]).view(1,1,3,3))
   self.register_buffer('rgb_mean',torch.tensor([.485,.456,.406]).view(1,3,1,1))
   self.register_buffer('rgb_std',torch.tensor([.229,.224,.225]).view(1,3,1,1))
   self.register_buffer('luminance',torch.tensor([.299,.587,.114]).view(1,3,1,1))
  self.head=nn.Linear(128,11)
 def forward(self,x):
  feat=self.cnn(x)
  if self.exp=='N02':
   weights=self.height_score(feat).softmax(dim=2); feat=(feat*weights).sum(dim=2); z=feat
  elif self.exp=='N07':
   rgb=x*self.rgb_std+self.rgb_mean; gray=(rgb*self.luminance).sum(dim=1,keepdim=True)
   gx=torch.nn.functional.conv2d(gray,self.sobel_x,padding=1); gy=torch.nn.functional.conv2d(gray,self.sobel_y,padding=1)
   edge=torch.sqrt(gx.square()+gy.square()+1e-6); edge_feat=self.edge_cnn(edge)
   if edge_feat.shape[2:]!=feat.shape[2:]: raise RuntimeError('Sobel feature branch does not align with RGB feature map')
   z=torch.cat([feat,edge_feat],dim=1).mean(2)
   z=torch.nn.functional.silu(self.temporal_projection(z))
  else: z=feat.mean(2)
  z=z.contiguous()
  if self.exp=='N02': z=torch.nn.functional.silu(self.temporal(z.transpose(1,2))).transpose(1,2)
  elif self.exp=='N04':
   z3=self.temporal3(z.transpose(1,2)); z5=self.temporal5(z.transpose(1,2)); z=torch.nn.functional.silu(z3+z5).transpose(1,2)
  elif self.exp=='N07': z=torch.nn.functional.silu(self.temporal(z.transpose(1,2))).transpose(1,2)
  return self.head(z).log_softmax(-1)

@torch.no_grad()
def predict(model,loader,device):
 model.eval(); out=[]
 for x,_,_,names,truths,widths in loader:
  z=model(x.to(device)); lens=torch.div(widths+3,4,rounding_mode='floor').clamp(max=z.shape[1]).tolist(); seq=z.argmax(-1).cpu().tolist()
  for name,truth,s,T in zip(names,truths,seq,lens):
   pred=[]; prev=0
   for k in s[:T]:
    if k and k!=prev: pred.append(str(k-1))
    prev=k
   out.append({'sample_id':name,'truth':truth,'prediction':''.join(pred),'input_timesteps':T})
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--experiment',choices=list(SPECS),required=True); ap.add_argument('--output-root',default='/media/gmo/linhnx/workspace/workdir_Research/results/lightocr_n02_n04_n07_20261018_screen01'); ap.add_argument('--epochs',type=int,default=50); ap.add_argument('--patience',type=int,default=10); ap.add_argument('--batch-size',type=int,default=32); ap.add_argument('--workers',type=int,default=4); ap.add_argument('--seed',type=int,default=42); a=ap.parse_args()
 if not torch.cuda.is_available(): raise RuntimeError('CUDA unavailable; refusing CPU fallback')
 device=torch.device('cuda'); out=Path(a.output_root)/a.experiment; out.mkdir(parents=True,exist_ok=True)
 sys.stdout=open(out/'train.log','a',buffering=1); sys.stderr=sys.stdout
 labels=readj(DATA/'train_label.json'); tr=sum((ids(CACHE/f'base_fit_fold_{k}.jsonl') for k in range(5)),[]); dv=ids(CACHE/'model_dev.jsonl')
 if (len(tr),len(dv))!=(1467,244) or set(tr)&set(dv): raise RuntimeError('frozen split audit failed')
 if any(i not in labels for i in tr+dv): raise RuntimeError('missing labels on frozen train/dev IDs')
 if any(not labels[i] or any(c not in CHARS for c in labels[i]) for i in tr+dv): raise RuntimeError('unexpected/empty target string')
 # Pilot 007's experimental split is independent of the source archive's physical train/valid folders.
 # Resolve each frozen ID by basename across only those two source folders; never read test/cross-data.
 image_paths={}; source_counts={'train':0,'valid':0}; missing=[]; ambiguous=[]
 for name in sorted(set(tr+dv)):
  matches=[(split,DATA/split/name) for split in ('train','valid') if (DATA/split/name).is_file()]
  if len(matches)==0: missing.append(name)
  elif len(matches)>1: ambiguous.append({'sample_id':name,'source_paths':[str(p.relative_to(WD/'data')) for _,p in matches]})
  else:
   split,p=matches[0]; image_paths[name]=p; source_counts[split]+=1
 data_audit={'status':'passed' if not missing and not ambiguous else 'failed','experimental_train_n':len(tr),'experimental_dev_n':len(dv),'physical_source_counts':source_counts,'missing_ids':missing,'ambiguous_ids':ambiguous,'lookup_folders':['data/Indomain_curated/crops/train','data/Indomain_curated/crops/valid'],'test_and_cross_data_read':False}
 save(out/'data_file_audit.json',data_audit)
 if missing or ambiguous: raise RuntimeError(f"image resolution failed: missing={len(missing)}, ambiguous={len(ambiguous)}; see data_file_audit.json")
 train_ds=Crops(tr,labels,image_paths); dev_ds=Crops(dv,labels,image_paths)
 dev_loader=DataLoader(dev_ds,batch_size=a.batch_size,shuffle=False,num_workers=a.workers,pin_memory=True,collate_fn=collate)
 train_loader=DataLoader(train_ds,batch_size=a.batch_size,shuffle=True,num_workers=a.workers,pin_memory=True,collate_fn=collate)
 model=Network(a.experiment).to(device); params=sum(p.numel() for p in model.parameters())
 # Audit CTC feasibility before training; every image is retained, and invalid rows fail loudly.
 invalid=[]
 for _,y,yl,names,_,widths in DataLoader(train_ds,batch_size=64,shuffle=False,num_workers=0,collate_fn=collate):
  for name,L,w in zip(names,yl.tolist(),widths.tolist()):
   text=labels[name]; repeated=sum(text[i]==text[i-1] for i in range(1,len(text))); T=(w+3)//4
   if T<L+repeated: invalid.append({'sample_id':name,'T':T,'required':L+repeated})
 if invalid: save(out/'ctc_invalid_samples.json',invalid); raise RuntimeError(f'{len(invalid)} CTC-infeasible train examples; run stopped without dropping them')
 cfg={'experiment':a.experiment,'name':SPECS[a.experiment]['name'],'status':'running','evidence':'exploratory; previously exposed Pilot 007 train/model-dev split','seed':a.seed,'epochs':a.epochs,'patience':a.patience,'batch_size':a.batch_size,'input':'RGB 32x192; aspect resize; right pad; ImageNet normalization','vocabulary':list(CHARS),'ctc_blank':0,'loss':'CTC','optimizer':'AdamW lr=0.001 weight_decay=0.0001','selection':'lowest dev CER; exact-match tie-break','train_n':len(tr),'dev_n':len(dv),'params':params,'gpu':torch.cuda.get_device_name(0),'torch':torch.__version__,'train_labels_sha256':sha(DATA/'train_label.json'),'pilot007_cache_manifest_sha256':sha(CACHE/'manifest.json'),'source_head':subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(),'source_status':subprocess.run(['git','-C',str(ROOT),'status','--short'],capture_output=True,text=True).stdout.splitlines()}
 cfg['image_resolution']='unique basename in source train/valid folders; experimental train/dev IDs remain the frozen Pilot 007 lists'
 cfg['physical_image_source_counts']=source_counts
 save(out/'config.json',cfg); save(out/'manifest.json',{'config':cfg,'train_ids':tr,'dev_ids':dv,'image_source_split':{name:str(p.relative_to(DATA)) for name,p in image_paths.items()}})
 random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed); torch.cuda.manual_seed_all(a.seed); gen=torch.Generator().manual_seed(a.seed)
 train_loader=DataLoader(train_ds,batch_size=a.batch_size,shuffle=True,generator=gen,num_workers=a.workers,pin_memory=True,collate_fn=collate)
 opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4); sch=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=a.epochs); lossfn=nn.CTCLoss(blank=0,zero_infinity=False); scaler=torch.cuda.amp.GradScaler()
 best=(float('inf'),-1); stale=0; hist=[]; t0=time.time()
 for ep in range(1,a.epochs+1):
  model.train(); losses=[]
  for x,y,yl,names,truths,widths in train_loader:
   x=x.to(device,non_blocking=True); y=y.to(device); yl=yl.to(device); opt.zero_grad(set_to_none=True)
   with torch.cuda.amp.autocast(): z=model(x)
   il=((widths.to(device)+3)//4).long()
   need=yl+torch.tensor([sum(text[i]==text[i-1] for i in range(1,len(text))) for text in truths],device=device)
   if torch.any(il<need): raise RuntimeError('CTC length audit failed in batch')
   loss=lossfn(z.float().transpose(0,1),y,il,yl)
   if not torch.isfinite(loss): raise RuntimeError('non-finite CTC loss')
   scaler.scale(loss).backward(); scaler.unscale_(opt); nn.utils.clip_grad_norm_(model.parameters(),5); scaler.step(opt); scaler.update(); losses.append(float(loss.detach().cpu()))
  sch.step(); rows=predict(model,dev_loader,device); m=metrics(rows); rec={'epoch':ep,'train_loss':float(np.mean(losses)),'dev_cer':m['cer'],'dev_exact_match':m['exact_match'],'seconds':time.time()-t0}; hist.append(rec)
  with open(out/'train_history.csv','w',newline='') as f: w=csv.DictWriter(f,fieldnames=hist[0].keys()); w.writeheader(); w.writerows(hist)
  if (m['cer'],-m['exact_match'])<best:
   best=(m['cer'],-m['exact_match']); stale=0; torch.save({'state':model.state_dict(),'experiment':a.experiment,'seed':a.seed,'epoch':ep,'params':params},out/'best.pt'); jsonl(out/'model_dev_predictions.jsonl',rows)
  else: stale+=1
  save(out/'progress.json',{'status':'running','experiment':a.experiment,'seed':a.seed,'epoch':ep,'best_epoch':ep-stale,'latest_dev':m,'elapsed_s':time.time()-t0})
  print(json.dumps(rec),flush=True)
  if stale>=a.patience: break
 final=[json.loads(x) for x in (out/'model_dev_predictions.jsonl').read_text().splitlines()]; result={'status':'completed','experiment':a.experiment,'seed':a.seed,'best_epoch':ep-stale,'params':params,'model_dev':metrics(final),'checkpoint_sha256':sha(out/'best.pt'),'elapsed_s':time.time()-t0,'artifact_path':str(out)}
 save(out/'result.json',result); save(Path(a.output_root)/f'{a.experiment}_summary.json',result); print(json.dumps(result),flush=True)
if __name__=='__main__': main()
