#!/usr/bin/env python
from sys import argv
import json, os, shutil, time

try:
    import lz4.block as lz4
except ImportError:
    import lz4

with open(argv[1], "rb") as input_lz4:
    if input_lz4.read(8) != b"mozLz40\0":
        print("doesn't appear to be a mozilla lz4 file")
        exit()

    read_file = input_lz4.read()
    try:
        decompressed = lz4.decompress(read_file)
    except Exception as ex:
        print("failure to decompress json file: %s", ex)
        exit()

    try:
        session_json = json.loads(decompressed)
    except Exception as ex:
        print("failure to load decompressed json: %s", ex)
        exit()

    file_name = os.path.basename(argv[1])
    bakfile_name = argv[1] + "-" + str(int(time.time())) + "-" + file_name + ".bak"
    try:
        shutil.copyfile(argv[1], bakfile_name)
        print("backup jsonlz4 file written to " + bakfile_name)
    except Exception as ex:
        print("failure to backup original jsonlz4 file: %s", ex)
        exit()

    inspection_file_name = "original_session_for_inspection.json"
    with open(inspection_file_name, "w") as inspection_file:
        json.dump(session_json, inspection_file)
        print(
            "original session json written to "
            + inspection_file_name
            + " for inspection"
        )


for window in session_json["windows"]:
    for_removal = []
    for key, value in window["extData"].items():
        if isinstance(key, str) and str(key).startswith(
            "extension:treestyletab@piro.sakura.ne.jp:"
        ):
            for_removal.append(key)
        # if key == "extension:treestyletab@piro.sakura.ne.jp:tree-structure":
        #     del window["extData"][
        #         "extension:treestyletab@piro.sakura.ne.jp:tree-structure"
        #     ]
    for key in for_removal:
        del window["extData"][key]

inspection_file_name = "modified_session_for_inspection.json"
with open(inspection_file_name, "w") as inspection_file:
    json.dump(session_json, inspection_file)
    print(
        "modified session json written to " + inspection_file_name + " for inspection"
    )

ss_file_name = "sessionstore.jsonlz4"
with open(ss_file_name, "wb") as compressed_file:
    compressed_file.write(
        b"mozLz40\0"
        + lz4.compress(bytes(json.dumps(session_json, separators=(",", ":")), "utf-8"))
    )
    print(
        "compressed session file written to "
        + ss_file_name
        + " for replacing original in profile folder"
    )
