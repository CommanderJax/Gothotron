from data_curator import EnglishDataCurator

if __name__ == '__main__':

    ouinfo_path = ''
    data_path = ''
    dc = EnglishDataCurator(ouinfo_path, data_path)
    dc.process_ouinfo()
