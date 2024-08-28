import argparse

def main():
    parser = argparse.ArgumentParser(description="argparse example")

    # the target file to be read, required and must be the first argument
    parser.add_argument('target', type=str, help='The target file to be read.')

    # -o or --output option, the output file to be written, optional
    parser.add_argument('-o', "--output", type=str, help='The output file to be written.')

    group = parser.add_mutually_exclusive_group()
    # -r or --run-py option, whether to run the target file as python script
    group.add_argument('-r', '--run-py', action='store_true', help='Whether to run the target file as python script.')
 
    # -R or --run-py-del option, whether to run the target file as python script and delete the target file, conflicts with -r option
    group.add_argument('-R', '--run-py-del', action='store_true', help='Whether to run the target file as python script and delete the target file.')

    args = parser.parse_args()


    # read the target file
    content = ''
    with open(args.target, 'r') as f:
        content = f.read()
    
    # separate the content by line
    lines = content.split('\n')

 
    



if __name__ == '__main__':
    main()

    
 
