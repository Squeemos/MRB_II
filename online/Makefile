update: svn pip web
	@echo "Updating all..."

svn:
	@echo "Updating svn..."
	svn update

pip:
	@echo "Installing and update packages..."
	pip install -e .
	pip install -r requirements.txt

web:
	@echo "Reloading web app..."
	touch ../../var/www/squeemos_pythonanywhere_com_wsgi.py
