#!/usr/bin/env python3
"""Genera los prompts del comité para una tesis, respetando la ceguera de cada agente.

Uso: python3 scripts/comite.py tesis/<TICKER>.md <dir_salida>
Crea <dir_salida>/bajista_<TICKER>.txt (solo tesis cualitativa + invalidación) y
<dir_salida>/valorador_<TICKER>.txt (solo ticker, nombre, bolsa, divisa).
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import cartera as C

def seccion(txt, titulo):
    m = re.search(r"^## " + re.escape(titulo) + r"[^\n]*\n(.*?)(?=^## |\Z)", txt, re.S | re.M)
    return m.group(1).strip() if m else ""

def main():
    path, out = sys.argv[1], sys.argv[2]
    txt = open(path, encoding="utf-8").read()
    ev = json.loads(re.search(r"```ev\s*\n(.*?)\n```", txt, re.S).group(1))
    t, mk = ev["ticker"], ev["mercado"]; m = C.MERCADOS[mk]
    nombre = re.match(r"# (.+?) \(", txt).group(1).strip()
    fecha = C.now().strftime("%d/%m/%Y")
    tesis = seccion(txt, "Tesis (cualitativa)"); inval = seccion(txt, "Condiciones de invalidación")
    # Por seguridad, quita cualquier cifra de TIR/EV que se haya colado en la tesis cualitativa
    tesis = re.sub(r"(?i)(TIR|EV|retorno esperado)[^\n]*", "[omitido]", tesis)
    def cuerpo(f):
        s = open(os.path.join(ROOT, "comite", f), encoding="utf-8").read()
        return s.split("---", 1)[1].strip()
    b = cuerpo("bajista.md").replace("{FECHA}", fecha).replace("{NOMBRE}", nombre).replace("{TICKER}", t).replace("{BOLSA}", mk) \
        .replace("{TESIS_CUALITATIVA}", tesis).replace("{INVALIDACION}", inval)
    v = cuerpo("valorador_ciego.md").replace("{FECHA}", fecha).replace("{NOMBRE}", nombre).replace("{TICKER}", t).replace("{BOLSA}", mk) \
        .replace("{DIVISA}", m["divisa"]).replace("{UNIDAD}", m["unidad_precio"])
    extra = ("\n\nNo modifiques ni crees ficheros en /home/user/Cartera-value. Puedes consultar el precio con "
             f"`cd /home/user/Cartera-value && python3 scripts/cartera.py precio {t}`. Tu respuesta final es tu informe completo.")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, f"bajista_{t}.txt"), "w").write(b + extra)
    open(os.path.join(out, f"valorador_{t}.txt"), "w").write(v + extra)
    print(f"ok {t}: bajista {len(b)} chars, valorador {len(v)} chars")

if __name__ == "__main__":
    main()
