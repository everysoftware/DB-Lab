import random
import os.path
import shutil

DELIMITER = '|'


class Database:
    def __init__(self, file='', headers=None):
        self.file = ''
        self.headers = []
        self.data = {}
        if headers is not None:
            self.create(file, headers)
        elif os.path.isfile(file):
            self.open(file)

    def create(self, file, headers):
        with open(file, 'w') as f:
            f.write(DELIMITER.join(headers) + '\n')
        self.open(file)

    def import_from_file(self, file):
        with open(file) as f:
            self.headers = f.readline().strip().split(DELIMITER)
            values = [line.strip().split(DELIMITER) for line in f.readlines()]
            self.data = {i[0]: dict(zip(self.headers[1:], i[1:])) for i in values}

    def open(self, file):
        self.import_from_file(file)
        self.file = file

    def update_file(self):
        with open(self.file, 'w') as f:
            s = DELIMITER.join(self.headers) + '\n'
            for i in self.data:
                s += DELIMITER.join([i] + list(self.data[i].values())) + '\n'
            f.write(s)
        self.open(self.file)

    def add(self, data):
        with open(self.file, 'a') as f:
            s = ''
            for i in data:
                if i in self.data:
                    print(f'Could not add {i} ({self.data[i]}): data already in database')
                else:
                    s += DELIMITER.join([i] + list(data[i].values())) + '\n'
                    self.data[i] = data[i]
            f.write(s)
        self.open(self.file)

    def get_by_header(self, header):
        return [self.data[i][header] for i in self.data]

    def get_by_id(self, data_id):
        return self.data[data_id]

    def del_by_id(self, data_id):
        self.data.pop(data_id)
        self.update_file()

    def modify(self, data):
        for i in data:
            if data[i] == self.data[i]:
                print(f'Could not modify {i} ({data[i]}): identical data')
                continue
            for header in data[i]:
                if data[i][header] == self.data[i][header]:
                    print(f'Could not modify {i}->{header} ({data[i]}): identical data')
                    continue
                self.data[i][header] = data[i][header]
        self.update_file()

    def create_backup(self, file):
        shutil.copy(self.file, file)

    def auto_id(self):
        return str(max(map(int, self.data.keys())) + 1)


def parse_list(file, db):
    rows = {}
    with open(file, encoding='utf-8') as f:
        data_id = 1
        for line in f:
            rows[str(data_id)] = dict(zip(db.headers[1:], line.strip().split(' ')))
            data_id += 1
    db.add(rows)


students_db = Database('students.db', ['id', 'name', 'surname', 'patronymic'])
variants_db = Database('variants.db', ['id', 'path_to_file'])
testing_table = Database('testing_table.db', ['student_id', 'variant_id'])
gen_table = Database('gen_table.db', ['id', 'full_name', 'path_to_file'])


def gen_distribution():
    return {student_id: {'variant_id': random.choice(list(variants_db.data.keys()))}
            for student_id in students_db.data}


def get_pretty_distribution():
    rows = {}
    data_id = 1
    for student_id in testing_table.data:
        var_id = testing_table.get_by_id(student_id)['variant_id']
        rows[str(data_id)] = {'full_name': ' '.join(students_db.get_by_id(student_id).values()),
                              'path_to_file': variants_db.get_by_id(var_id)['path_to_file']}
        data_id += 1
    return rows


parse_list('names.txt', students_db)
parse_list('variants.txt', variants_db)
testing_table.add(gen_distribution())
gen_table.add(get_pretty_distribution())

for row_id in gen_table.data:
    print(*gen_table.get_by_id(row_id).values())

empty_db = Database('empty.db', [])

students_db.create_backup('students_backup.db')

students_db.del_by_id('1')
students_db.del_by_id('5')

students_db.add({students_db.auto_id(): {'name': 'Новый', 'surname': 'Чел', 'patronymic': 'Челович1'}})
students_db.add({'95': {'name': 'Новый', 'surname': 'Чел', 'patronymic': 'Челович1'}})
students_db.add({'96': {'name': 'Новый', 'surname': 'Чел', 'patronymic': 'Челович2'}})
students_db.add({'96': {'name': 'Новый', 'surname': 'Чел', 'patronymic': 'Челович2'}})

students_db.modify({'6': {'name': 'ЧАСТИЧНЫЙ', 'surname': 'АПДЕЙТ'}})
students_db.modify({'6': {'name': 'ЧАСТИЧНЫЙ', 'surname': 'АПДЕЙТ'}})
students_db.modify({'8': {'name': 'ПОЛНЫЙ', 'surname': 'АПДЕЙТ', 'patronymic': '!!!'}})
students_db.modify({'8': {'name': 'ПОЛНЫЙ', 'surname': 'АПДЕЙТ', 'patronymic': '!!!'}})

students_db.import_from_file('students_backup.db')
# Раскомментить, чтобы увидеть исходный файл
# students_db.update_file()
