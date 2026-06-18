import base64, pathlib

b64 = base64.b64encode(pathlib.Path("lumenor.png").read_bytes()).decode()
uri = "data:image/png;base64," + b64

out = pathlib.Path("src/components/_logo_const.py")
out.write_text(
    "# Lumenor logo baked as base64 - auto-generated, do not edit\n"
    f'LUMENOR_B64 = "{b64}"\n'
    f'LUMENOR_DATA_URI = "{uri}"\n'
)
print("OK, length:", len(b64))
