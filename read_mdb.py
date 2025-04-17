import zipfile
import tempfile
import pyodbc
import os
import polars as pl

#настройки
file_list = os.listdir('//corp.tele2.ru/cpfolders/STAT.CP.Reports/Weekly_HWInventory/Nokia/')
zip_code = 'NS'

def file_verification() -> bool:

    temp_file = os.listdir('temp')
    if (file_list[-1][:-8] + '.xlsx') in temp_file:
        return True


def read_hw_inventory():

    # Путь к ZIP-архиву, выбирается последний архив из папки
    zip_path = '//corp.tele2.ru/cpfolders/STAT.CP.Reports/Weekly_HWInventory/Nokia/' + file_list[-1]
    mdb_filename = file_list[-1][:-4]
    # Открываем ZIP-архив. Сохранение временного файла
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        mdb_data = zip_ref.read(mdb_filename)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mdb') as temp_mdb_file:
        temp_mdb_file.write(mdb_data)
        temp_mdb_path = temp_mdb_file.name

    # Подключаемся к временному файлу MDB (Windows)
    conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={temp_mdb_path};'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    tables = [row.table_name for row in cursor.tables(tableType='TABLE')]

    table_to_select = 'mdb'
    columns_to_select = ['Region', 'SiteName', 'inventoryUnitType']
    filter_condition = "Region = '" + zip_code + "'"

    # Проверяем, существует ли указанная таблица
    if table_to_select in tables:
        columns_str = ', '.join(columns_to_select)

        query = f'SELECT {columns_str} FROM {table_to_select} WHERE {filter_condition}'
        df_pl = pl.read_database(query=query, connection=conn)
        df_pl.write_excel('temp/'+file_list[-1][:-8] + '.xlsx')

        print(f'DataFrame из таблицы {table_to_select, file_list[-1]}:')
        print(df_pl)
    else:
        print(f'Таблица {table_to_select} не найдена в базе данных.')

    cursor.close()
    conn.close()

    #clear_memory
    os.remove(temp_mdb_path)
    del mdb_data
    del temp_mdb_file

print(read_hw_inventory())


