from flask import render_template, request, redirect, url_for, abort, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required, LoginManager, UserMixin
from app.models import User, ChangeLog  # Import User and ChangeLog models from your SQLAlchemy setup
from sqlalchemy import or_

# Initialize login manager
login_manager = LoginManager()

# Required for Flask-Login
@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))  # Load the user from the database using SQLAlchemy

def init_app(app, db):

    login_manager.init_app(app)

    @app.route('/', methods=['GET'])
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')



    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = generate_password_hash(request.form['password'], method='sha256')
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')
    
    @app.route('/dashboard', methods=['GET'])
    @login_required
    def dashboard():
        query = request.args.get('q')
        if query:
            # Se c'è una query di ricerca, esegui la ricerca
            changes = ChangeLog.query.filter(
                (ChangeLog.title.ilike(f'%{query}%')) |
                (ChangeLog.customer_name.ilike(f'%{query}%')) |
                (ChangeLog.ga4_code.ilike(f'%{query}%'))
            ).all()
        else:
            # Altrimenti, ottieni tutti i cambiamenti
            changes = ChangeLog.query.all()
    
        if request.is_xhr:  # Controlla se la richiesta è una chiamata AJAX
            # Restituisci solo i dati dei risultati della ricerca come risposta JSON
            return jsonify(changes=[change.serialize() for change in changes])
    
        # Se non è una chiamata AJAX, restituisci la pagina HTML normale
        return render_template('dashboard.html', changes=changes, current_user_id=current_user.id, User=User)


    
    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_change():
        if request.method == 'POST':
            title = request.form['title']
            customer_name = request.form['customer_name']
            ga4_code = request.form['ga4_code']
            new_change = ChangeLog(title=title, customer_name=customer_name, ga4_code=ga4_code, user=current_user)
            db.session.add(new_change)
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template('add_change.html')
    
    
    @app.route('/edit/<int:change_id>', methods=['GET', 'POST'])
    @login_required
    def edit_change(change_id):
        change = ChangeLog.query.get_or_404(change_id)
        if current_user.is_admin or current_user.id == change.user_id:
            # Handle editing the changelog here
            # You can use the same form for adding changes
            if request.method == 'POST':
                change.title = request.form['title']
                change.customer_name = request.form['customer_name']
                change.ga4_code = request.form['ga4_code']
                db.session.commit()
                flash('ChangeLog updated successfully', 'success')
                return redirect(url_for('dashboard'))
            return render_template('edit_change.html', change=change)
        else:
            abort(403)  # Forbidden

    @app.route('/delete/<int:change_id>', methods=['GET', 'POST'])
    @login_required
    def delete_change(change_id):
        change = ChangeLog.query.get_or_404(change_id)
        if current_user.is_admin or current_user.id == change.user_id:
            # Handle deleting the changelog here
            db.session.delete(change)
            db.session.commit()
            flash('ChangeLog deleted successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            abort(403)  # Forbidden    
    
    

    
    
    @app.route('/api/search', methods=['GET'])
    def search():
        query = request.args.get('q')
        limit = request.args.get('limit', default=10, type=int)
        if not query:
            return jsonify({"message": "Query parameter is required"}), 400

        # Search in ChangeLog model
        changelog_results = ChangeLog.query.filter(
            or_(
                ChangeLog.title.ilike(f"%{query}%"),
                ChangeLog.customer_name.ilike(f"%{query}%"),
                ChangeLog.ga4_code.ilike(f"%{query}%")
            )
        ).limit(limit).all()

        # Serialize results
        changelog_data = [{"id": item.id, "title": item.title, "customer_name": item.customer_name, "ga4_code": item.ga4_code} for item in changelog_results]

        return jsonify({"results": changelog_data})
    
    
    
    
    
    
    @app.route('/logout', methods=['GET'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
