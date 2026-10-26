"""Monocular depth for the Symz avatar art (Depth-Anything-V2 small, ONNX), used by blender/symz_fig.py.
Model: https://github.com/fabio-sim/Depth-Anything-ONNX/releases (depth_anything_v2_vits.onnx).
usage: python3 depth_symz.py depth_anything_v2_vits.onnx ../img/avatar-3d.png avatar_depth.npy"""
import sys, numpy as np, cv2, onnxruntime as ort
from PIL import Image
model, src, out = sys.argv[1:4]
s = ort.InferenceSession(model); name = s.get_inputs()[0].name
im = Image.open(src).convert('RGBA'); W, H = im.size
sq = Image.new('RGBA', (H, H), (128, 128, 128, 255)); ox = (H - W) // 2; sq.alpha_composite(im, (ox, 0))   # pad to square
x = cv2.resize(np.asarray(sq.convert('RGB')).astype(np.float32) / 255, (518, 518), interpolation=cv2.INTER_AREA)
x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
d = np.squeeze(s.run(None, {name: x})[0]); d = cv2.resize(d, (H, H), interpolation=cv2.INTER_CUBIC)[:, ox:ox + W]
np.save(out, d); print('saved', out, d.shape)
