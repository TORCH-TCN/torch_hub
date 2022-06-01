from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required


users = Blueprint('users', __name__, url_prefix='/users')


@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        
        flash('Updated successfully!', category='success')

    return render_template('profile.html', user=current_user)
