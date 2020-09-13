from data_curator import EnglishDataCurator
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--ouinfo-path', type=str,
                        help='Path to your OUINFO.INF file.', required=True)

    args = parser.parse_args()
    dc = EnglishDataCurator(args.ouinfo_path)
    dc.generate_test_and_validation_datasets()


