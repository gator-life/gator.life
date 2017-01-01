# -*- coding: utf-8 -*-
from flask import Blueprint, render_template

react = Blueprint('react', __name__, template_folder='.')  # pylint: disable=invalid-name


@react.route('/react')
def home():
    return render_template('index.html')
