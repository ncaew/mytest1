1.generate
cd mytest1
xgettext -a --debug -o app.po --from-code utf-8 `find  guard/ -name "*.py"|xargs `

mkdir -p locale/zh_CN/LC_MESSAGES/
mv app.po locale/zh_CN/LC_MESSAGES/
cd locale/zh_CN/LC_MESSAGES/
edit app.po, fill msgstr under the msgid if you want to translate it
msgfmt -o app.mo app.po

2.use in python
import gettext

t = gettext.translation('app', 'locale', languages=['zh_CN'], fallback=True)
t.install()
_ = t.gettext
print(_('english'))

