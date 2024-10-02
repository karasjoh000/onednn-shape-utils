import argparse


def get_reorder_shape_str(conv_shape_dict, src=True):
    shape_str = ""
    shape_str += str(conv_shape_dict["mb"])
    # shape_str += "x" + str(conv_shape_dict["g"])
    if src:
        shape_str += "x" + str(conv_shape_dict["ic"])
        if "id" in conv_shape_dict.keys():
            shape_str += "x" + str(conv_shape_dict["id"])
        if "ih" in conv_shape_dict.keys():
            shape_str += "x" + str(conv_shape_dict["ih"])
        if "iw" in conv_shape_dict.keys():
            shape_str += "x" + str(conv_shape_dict["iw"])
    else:
        shape_str += "x" + str(conv_shape_dict["oc"])
        if "od" in conv_shape_dict.keys():
            shape_str += "x" + str(conv_shape_dict["od"])
        if "oh" in conv_shape_dict.keys():
            shape_str += "x" + str(conv_shape_dict["oh"])
        if "ow" in conv_shape_dict.keys():
            shape_str += "x" + str(conv_shape_dict["ow"])
    return shape_str


def compute_output_size(input_size, kernel_size, stride_size, padding_size):
    return ((input_size + padding_size - kernel_size) // stride_size) + 1


def parse_shape(conv_shape):
    if "n" in conv_shape:
        conv_shape = conv_shape.split("n")[0]
    # remove all '_' from string
    conv_shape = conv_shape.replace("_", "")
    # parse g1mb1ic4ih84oc16oh20kh8sh4ph0 into a dict that
    # looks like  {'g': 1, 'mb': 1, 'ic': 4, 'ih': 84, 'oc': 16, 'oh': 20,
    #              'kh': 8, 'sh': 4, 'ph': 0}
    conv_shape_dict = {}
    key = ""
    value = ""
    next = False
    for char in conv_shape:
        if char.isalpha() and not next:
            key += char
        elif char.isalpha() and next:
            conv_shape_dict[key] = int(value)
            next = False
            key = char
            value = ""
        elif char.isdigit():
            value += char
            next = True
    conv_shape_dict[key] = int(value)
    if "g" not in conv_shape_dict.keys():
        conv_shape_dict["g"] = 1
    if "mb" not in conv_shape_dict.keys():
        conv_shape_dict["mb"] = 2
    if "iw" not in conv_shape_dict.keys():
        if "ih" not in conv_shape_dict.keys():
            conv_shape_dict["iw"] = conv_shape_dict["ih"] \
                = conv_shape_dict["id"]
        else:
            conv_shape_dict["iw"] = conv_shape_dict["ih"]
    if "kw" not in conv_shape_dict.keys():
        if "kh" not in conv_shape_dict.keys():
            if "kd" in conv_shape_dict.keys():
                conv_shape_dict["kw"] = conv_shape_dict["kh"] \
                    = conv_shape_dict["kd"]
            else:
                conv_shape_dict["kw"] = 1
                if "ih" in conv_shape_dict.keys():
                    conv_shape_dict["kh"] = 1
                if "id" in conv_shape_dict.keys():
                    conv_shape_dict["kd"] = 1
        else:
            conv_shape_dict["kw"] = conv_shape_dict["kh"]

    if "sw" not in conv_shape_dict.keys():
        if "sh" not in conv_shape_dict.keys():
            if "sd" in conv_shape_dict.keys():
                conv_shape_dict["sw"] = conv_shape_dict["sh"] \
                    = conv_shape_dict["sd"]
            else:
                conv_shape_dict["sw"] = 1
                if "sh" not in conv_shape_dict.keys():
                    conv_shape_dict["sh"] = 1
                if "sd" not in conv_shape_dict.keys():
                    conv_shape_dict["sd"] = 1
        else:
            conv_shape_dict["sw"] = conv_shape_dict["sh"]

    if "ow" not in conv_shape_dict.keys():
        if "oh" in conv_shape_dict.keys():
            conv_shape_dict["oh"] = conv_shape_dict["od"]
        elif "od" in conv_shape_dict.keys():
            conv_shape_dict["ow"] = conv_shape_dict["oh"] = \
                conv_shape_dict["od"]
        else:
            conv_shape_dict["ow"] = compute_output_size(
                conv_shape_dict["iw"], conv_shape_dict["kw"],
                conv_shape_dict["sw"],
                0 if "pw" not in conv_shape_dict.keys()
                else conv_shape_dict["pw"])
            if "ih" in conv_shape_dict.keys():
                conv_shape_dict["oh"] = compute_output_size(
                    conv_shape_dict["ih"], conv_shape_dict["kh"],
                    conv_shape_dict["sh"],
                    0 if "ph" not in conv_shape_dict.keys()
                    else conv_shape_dict["ph"])
            if "id" in conv_shape_dict.keys():
                conv_shape_dict["od"] = compute_output_size(
                    conv_shape_dict["id"], conv_shape_dict["kd"],
                    conv_shape_dict["sd"],
                    0 if "pd" not in conv_shape_dict.keys()
                    else conv_shape_dict["pd"])

    return conv_shape_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # accept input arg string such as
    # 'g1mb1ic4ih84oc16oh20kh8sh4ph0n"a3c:conv1"' or if
    # --batch flag is provided, this arguement is not needed.
    parser.add_argument('conv', type=str, help='convolution shape', nargs='?')
    parser.add_argument('--batch', type=str,
                        help='reorder to batch', required=False)
    # create a flag for dst
    parser.add_argument('--dst', dest='dst',
                        action='store_true', help='reorder to dst')
    args = parser.parse_args()
    if not args.batch:
        print(get_reorder_shape_str(parse_shape(args.conv), not args.dst))
    else:
        for line in open(args.batch, "r"):
            # if line only white space or has # in it, then skip.
            if line.isspace() or "#" in line:
                continue
            print(get_reorder_shape_str(parse_shape(line), not args.dst))
