# Phase 1 pretrained OCR teacher catalog

Status: teacher evaluation is in progress. No zero-shot OCR metric has been obtained yet. All model-development IDs are previously exposed and all results on them are exploratory.

## PP-OCRv5 Mobile Latin recognition

- Model API ID: `latin_PP-OCRv5_mobile_rec`.
- Selection reason: PaddleOCR's official model list explicitly says this PP-OCRv5 mobile Latin recognizer supports numeric text recognition. The published stored model size is 14 MB, so it is a teacher/comparator, not the approximately 1M-parameter student.
- Official model list and API: https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/module_usage/text_recognition.en.md
- Official model config: https://github.com/PaddlePaddle/PaddleOCR/blob/main/configs/rec/PP-OCRv5/PP-OCRv5_mobile_rec.yml
- Official pretrained training weights: https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/latin_PP-OCRv5_mobile_rec_pretrained.pdparams
- Official inference package: https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/latin_PP-OCRv5_mobile_rec_infer.tar
- The model-managed API returns `rec_text` and `rec_score`; primary evaluation must preserve that exact decoded string, including leading zeros. Any digit-only constrained decoder is a separate diagnostic.
- First attempt failed before a forward pass because shared Paddle GPU 2.6.2 lacks `AnalysisConfig.set_optimization_level`, required by installed PaddleOCR/PaddleX 3.7. This failure is logged in tracker row37; no metric was recorded. A separate Paddle 3.3 CUDA 11.8 virtualenv is being installed without changing the shared environment.
- Inference graph SHA-256 and exact `inference.yml` preprocessing/dictionary details remain pending inspection after the runtime is compatible.

## English SVTR-T CTC

- Model: official SVTR Tiny English CTC checkpoint `rec_svtr_tiny_none_ctc_en_train.tar`.
- Selection reason: official PaddleOCR documentation provides an English SVTR-T CTC training checkpoint/config and an English character dictionary, matching the user's requested SVTR comparator and CTC decoding.
- Official procedure and checkpoint URL: https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version2.x/algorithm/text_recognition/algorithm_rec_svtr.en.md
- Direct checkpoint archive: https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/rec_svtr_tiny_none_ctc_en_train.tar
- Verify the archive's config, image shape, dictionary contents/order, CTC blank index and checkpoint hashes before evaluation. Do not assume its default preprocessing matches the in-domain crops.

## Evaluation boundary

Use only the frozen 244-image model-development split for the initial teacher screen, and pass sample IDs/image paths—not labels—to inference. Independently reconstruct exact match and CER after inference. Do not access test/cross-data. Record source revision, resolved config, package versions, checkpoint hashes, raw sample predictions and failures in the run bundle and tracker. Do not call a model-development score independent validation.
