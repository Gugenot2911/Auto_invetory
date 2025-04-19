from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages
from werkzeug.utils import secure_filename
from config import Config
from file_processor import FileProcessor
import os
import polars as pl

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)


# Добавляем обработчик для фильтрации
def filter_data(df, filter_text):
    if filter_text:
        return df.filter(
            pl.col("Наименование, назначение и краткая характеристика объекта")
            .str.to_lowercase()
            .str.contains(filter_text.lower()))
    return df


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не был отправлен', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Не выбран файл для загрузки', 'error')
            return redirect(request.url)

        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in app.config[
            'ALLOWED_EXTENSIONS']:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if os.path.exists(filepath):
                os.remove(filepath)

            file.save(filepath)

            try:
                df = FileProcessor.process_inventory(filepath)
                if len(df) == 0:
                    raise ValueError("Файл не содержит данных для обработки")

                session['current_file'] = filename
                flash('Файл успешно загружен', 'success')
                return redirect(url_for('show_table'))

            except Exception as e:
                flash(f'Ошибка обработки файла: {str(e)}', 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)

        else:
            flash('Недопустимый формат файла. Разрешены только .xlsx и .xls', 'error')
            return redirect(request.url)

    return render_template('upload.html', messages=get_flashed_messages(with_categories=True))


@app.route('/table', methods=['GET', 'POST'])
def show_table():
    if 'current_file' not in session:
        flash('Файл не выбран', 'error')
        return redirect(url_for('upload_file'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['current_file'])
    if not os.path.exists(filepath):
        flash('Файл не найден', 'error')
        return redirect(url_for('upload_file'))

    try:
        df = FileProcessor.process_inventory(filepath)
        filter_text = request.form.get('filter', '') if request.method == 'POST' else ''

        filtered_df = filter_data(df, filter_text)

        return render_template(
            'table.html',
            filename=session['current_file'],
            columns=df.columns,
            records=filtered_df.to_dicts(),
            totals={
                'count': len(df),
                'initial': df['Первоначальная стоимость, руб.коп'].sum(),
                'residual': df['Остаточная балансовая стоимость,руб.коп'].sum()
            },
            filter_text=filter_text
        )

    except Exception as e:
        flash(f'Ошибка при отображении данных: {str(e)}', 'error')
        return redirect(url_for('upload_file'))


if __name__ == '__main__':
    app.run(debug=True)