# Read a file with a list of shapes.
# Each shape has the following format:
# 1, 2, 3, ..., n, -> 1, 2, 3, ..., n
import argparse


def create_shape(shape_csv):
    return [int(x) for x in shape_csv.split(',')]


def parse_reorder_line(line):
    order1 = line.split('->')[0].strip()
    order1 = create_shape(order1)
    order2 = line.split('->')[1].strip()
    order2 = create_shape(order2)
    return order1, order2


def compute_stride(reorder, shape):
    unordered_stride = [-1 for _ in range(len(shape))]
    for i in range(1, len(shape) + 1):
        #        print(i)
        if i == 1:
            unordered_stride[-i] = 1
        else:
            unordered_stride[-i] = shape[reorder[-(i-1)]] * \
                unordered_stride[-(i-1)]
    return unordered_stride


def create_strides(shape, reorder):
    # pre create list size of shape with -1
    strides1 = [-1 for _ in range(len(shape))]
    strides2 = [-1 for _ in range(len(shape))]
    reorder1 = reorder[0]
    reorder2 = reorder[1]
    unordered_stride1 = compute_stride(reorder1, shape)
    unordered_stride2 = compute_stride(reorder2, shape)
    for i in range(len(shape)):
        strides1[reorder1[i]] = unordered_stride1[i]
        strides2[reorder2[i]] = unordered_stride2[i]
    return strides1, strides2


def parse_file(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    # read first line
    shape = create_shape(lines[0].strip())
    # parse the rest of the lines skipping first line

    reorders = [parse_reorder_line(line) for line in lines[1:]]
    strides = [create_strides(shape, reorder) for reorder in reorders]
    return shape, strides, reorders


def shape_or_stride2str(shape):
    return "x".join(map(str, shape))


def create_reorder_str(reorder):
    return ', '.join(map(str, reorder[0])) + " -> " \
            + ', '.join(map(str, reorder[1]))


def print_reorders(shape, strides, reorders):
    print("# Shape: ", shape)
    for i in range(len(reorders)):
        print("# ", create_reorder_str(reorders[i]))
        print("--strides=" + shape_or_stride2str(
            strides[i][0]) + ":" + shape_or_stride2str(strides[i][1]))
        print(shape_or_stride2str(shape))


def main():
    parser = argparse.ArgumentParser(
        description='parse filepath')
    parser.add_argument('file', type=str, help='File name to parse')
    args = parser.parse_args()
    shape, strides, reorders = parse_file(args.file)
    print_reorders(shape, strides, reorders)


if __name__ == "__main__":
    main()
