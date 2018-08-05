# -*- coding: utf-8 -*-
# @Author: Clarence
# @Date:   2018-06-21 12:59:12
# @Last Modified by:   Clarence
# @Last Modified time: 2018-06-27 20:01:25
from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, abort, request
from flask_sqlalchemy import SQLAlchemy

from forms import NewsForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3308/net_news?charset=utf8'
app.config['SECRET_KEY'] = 'youaresherlock' # 用来防止跨站脚本攻击 随机的字符串
db = SQLAlchemy(app)

class News(db.Model):
	'''新闻类型'''
	__tablename__ = 'news'
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(200), nullable = False)
	content = db.Column(db.String(2000), nullable = False)
	types = db.Column(db.String(10), nullable = False)
	image = db.Column(db.String(300))
	author = db.Column(db.String(20))
	view_count = db.Column(db.Integer)
	created_at = db.Column(db.DateTime)
	is_valid = db.Column(db.Boolean)

	def __repr__(self):
		return '<News %r>' % self.content

# News.metadata.create_all()

@app.route('/')
def index():
	'''新闻的首页'''
	#news_list = News.query.all()
	news_list = News.query.filter_by(is_valid = 1)
	return render_template('index.html', news_list = news_list)

@app.route('/cat/<name>/')
def cat(name):
	'''新闻的类别'''
	# 查询类别为name的新闻数据
	news_list = News.query.filter_by(is_valid = 1, types = name)
	return render_template('cat.html', name = name, news_list = news_list)

# id必须是整形int
@app.route('/detail/<int:pk>/')
def detail(pk):
	'''新闻详情信息'''
	new_obj = News.query.get(pk) #获得指定id的新闻纪录
	return render_template('detail.html', new_obj = new_obj)


@app.route('/admin/')
@app.route('/admin/<int:page>/')
def admin(page=None):
	'''后台管理首页, page表示当前页,per_page表示每页有几条记录'''
	if page is None:
		page = 1
	# is_valid表示有效数据，用户删除掉的数据在数据库中字段is_valid是False
	page_data = News.query.filter_by(is_valid = 1).paginate(page = page, per_page = 4)
	return render_template('admin/index.html', page_data = page_data)

@app.route('/admin/add', methods = ('GET', 'POST'))
def add():
	'''新闻新增'''
	form = NewsForm()
	if form.validate_on_submit():
		# 获取用户输入表达中的数据
		# 保存数据
		n1 = News(
			title = form.title.data,
			content = form.content.data,
			image = form.image.data,
			types = form.news_type.data,
			created_at = datetime.now(),
			is_valid = 1)
		db.session.add(n1)
		db.session.commit()
		# 文字提示flash
		flash('新增成功!')
		return redirect(url_for('admin')) #新增加入数据库之后重定向到首页
	return render_template('admin/add.html', form = form)

@app.route('/admin/update/<int:pk>/', methods = ('GET', 'POST'))
def update(pk):
	'''修改新闻信息'''
	new_obj = News.query.get(pk) 
	# 如果没有数据，则返回404 Not Found
	if new_obj is None:
		abort(404)
	form  = NewsForm(obj = new_obj)
	if form.validate_on_submit():
		new_obj.title = form.title.data
		new_obj.content = form.content.data
		new_obj.types = form.news_type.data
		new_obj.image = form.image.data

		db.session.add(new_obj)
		db.session.commit()
		flash('修改成功')
		return redirect(url_for('admin'))
	return render_template('admin/update.html', form = form)

@app.route('/admin/delete/<int:pk>/', methods=['POST'])
def delete(pk):
	'''删除新闻内容，逻辑删除，数据中的数据并没有删除，可以将is_valid标记设置为0'''
	if request.method == 'POST':
		obj = News.query.get(pk)
		if obj is None:
			return '失败'
		obj.is_valid = False
		db.session.add(obj)
		db.session.commit()
		return '成功'
	return '失败'



if __name__ == '__main__':
	app.run(debug = True)



   