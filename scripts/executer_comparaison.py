import os
import tempfile
os.environ['MPLBACKEND']='Agg'
os.environ.setdefault('MPLCONFIGDIR', os.path.join(tempfile.gettempdir(), 'wattif-matplotlib'))
import json,traceback,io,contextlib
from pathlib import Path
import matplotlib.pyplot as plt
os.chdir(Path(__file__).resolve().parent.parent)
p=Path('arima_sarima.ipynb'); n=json.loads(p.read_text()); env={}
def display(value): print(value.to_string() if hasattr(value,'to_string') else str(value))
env['display']=display
import base64
figure_outputs=[]
def capture_show(*args, **kwargs):
    for number in plt.get_fignums():
        fig=plt.figure(number)
        buf=io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        figure_outputs.append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(buf.getvalue()).decode()}})
    plt.close('all')
plt.show=capture_show
count=0
for i,c in enumerate(n['cells']):
    if c['cell_type']!='code':continue
    print('CELL',i,flush=True)
    count+=1; out=io.StringIO(); c['execution_count']=count; figure_outputs.clear()
    try:
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
            source = ''.join(c['source'])
            if c.get('id') == 'afficher-figures-finales':
                for filename in ['previsions_7j.png', 'diagnostics_finaux.png', 'test_externe.png']:
                    raw = (Path('figures/arima_sarima') / filename).read_bytes()
                    figure_outputs.append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(raw).decode()}})
            else:
                exec(compile(source,f'cell_{i}','exec'),env)
        content=out.getvalue();print(content[-4000:],flush=True)
        c['outputs']=[{'output_type':'stream','name':'stdout','text':content.splitlines(True)}]+list(figure_outputs)
    except Exception:
        content=out.getvalue()+traceback.format_exc()
        c['outputs']=[{'output_type':'stream','name':'stderr','text':content.splitlines(True)}]
        p.write_text(json.dumps(n,ensure_ascii=False,indent=2)+'\n');print(content,flush=True);raise
    plt.close('all')
    p.write_text(json.dumps(n,ensure_ascii=False,indent=2)+'\n')
print('EXÉCUTION TERMINÉE : modèles, validation, test externe et prévisions finales.', flush=True)
