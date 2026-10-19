# Design

The stem emits [B,C,H,T]. For column_projection, permute to [B,T,H,C], require H=2, flatten only the last two dimensions to [B,T,2C], then apply Linear(2C,C). This keeps the sequence axis and CTC frame count unchanged. The configuration intentionally binds this experiment to the audited 48-pixel input height; unsupported stem heights raise a ValueError. The projection is newly initialized and trained from scratch. No pretraining or distillation is introduced.
