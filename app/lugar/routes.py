from sqlite3 import IntegrityError
from flask import render_template, redirect, url_for, flash
from app import db
from app.lugar import bp
from app.lugar.forms import LugarForm
from app.lugar.models import Lugar
import pandas as pd
from io import BytesIO
from flask import send_file
 
@bp.route('/')
def index():
    lugares = Lugar.query.all()
    return render_template('lugar/index.html', lugares=lugares)
 
@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    form = LugarForm()
    if form.validate_on_submit():
        lugar = Lugar(nombre=form.nombre.data, codigo_postal=form.codigo_postal.data)
        db.session.add(lugar)
        db.session.commit()
        flash('Lugar creado con éxito.')
        return redirect(url_for('lugar.index'))
    return render_template('lugar/form.html', form=form)
 
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    lugar = Lugar.query.get_or_404(id)
    form = LugarForm(obj=lugar)
    if form.validate_on_submit():
        form.populate_obj(lugar)
        db.session.commit()
        flash('Lugar actualizado con éxito.')
        return redirect(url_for('lugar.index'))
    return render_template('lugar/form.html', form=form)
 
@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    lugar = Lugar.query.get_or_404(id)
    
    # Verificar si hay personas asociadas a este lugar
    if lugar.personas:
        flash('No puedes eliminar este lugar porque está asociado a una o más personas.', 'error')
        return redirect(url_for('lugar.index'))
 
    try:
        db.session.delete(lugar)
        db.session.commit()
        flash('Lugar eliminado con éxito.')
    except IntegrityError:
        db.session.rollback()
        flash('Error al eliminar el lugar.', 'error')
    
    return redirect(url_for('lugar.index'))

@bp.route('/exportar', methods=['GET'])
def exportar():
    lugares = Lugar.query.all()

    # Crear DataFrame con los datos de Lugares
    data = [{'id': lugar.id, 'Nombre': lugar.nombre, 'Código postal': lugar.codigo_postal} for lugar in lugares]
    df = pd.DataFrame(data)

    # Generar archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lugares')

    # Preparar el archivo para ser enviado al cliente
    output.seek(0)  # Colocar el puntero al inicio del archivo

    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='lugares_reporte.xlsx')