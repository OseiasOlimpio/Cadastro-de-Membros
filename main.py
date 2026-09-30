from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
import schemas
from typing import List
from datetime import date
from typing import Optional
from datetime import date as date_type
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=None)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {})


# ==== Cria membro ===#
@app.post("/membros")
def criar_membro(membro: schemas.MembroCreate, db: Session = Depends(get_db)):
    novo_membro = models.Membro(**membro.model_dump())
    db.add(novo_membro)
    db.commit()
    db.refresh(novo_membro)
    return novo_membro


# ==== Lista os membros ===#
@app.get("/membros", response_model=List[schemas.MembroResponse])
def listar_membros(db: Session = Depends(get_db)):
    return db.query(models.Membro).all()


# ====== Cria rota para visualizar membros =======
@app.get("/membros/visualizar", response_class=None)
def visualizar_membros(
    request: Request,
    busca: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Membro)

    if busca:
        query = query.filter(models.Membro.nome.ilike(f"%{busca}%"))
    if status:
        query = query.filter(models.Membro.status.ilike(status))
    membros = query.all()

    return templates.TemplateResponse(
        request,
        "listar.html",
        {"membros": membros, "busca": busca or "", "status_filtro": status or ""},
    )


@app.get("/membros/cadastrar", response_class=None)
def form_cadastrar(request: Request):
    return templates.TemplateResponse(request, "cadastrar.html", {})


@app.post("/membros/cadastrar", response_class=None)
def cadastrar_via_formulario(
    nome: str = Form(...),
    contato: str = Form(...),
    data_nascimento: Optional[date] = Form(None),
    funcao: Optional[str] = Form(None),
    status: str = Form("ativo"),
    db: Session = Depends(get_db),
):
    novo_membro = models.Membro(
        nome=nome,
        contato=contato,
        data_nascimento=data_nascimento,
        funcao=funcao,
        status=status,
    )
    db.add(novo_membro)
    db.commit()
    db.refresh(novo_membro)
    return RedirectResponse(url="/membros/visualizar", status_code=303)


@app.get("/membros/aniversariantes", response_class=None)
def aniversariantes_do_mes(request: Request, db: Session = Depends(get_db)):
    mes_atual = date_type.today().month
    todos_membros = db.query(models.Membro).all()

    aniversariantes = [
        m
        for m in todos_membros
        if m.data_nascimento and m.data_nascimento.month == mes_atual
    ]
    return templates.TemplateResponse(
        request, "aniversariantes.html", {"aniversariantes": aniversariantes}
    )


# ==== Pesquisa membro por Id ===#
@app.get("/membros/{membro_id}", response_model=schemas.MembroResponse)
def buscar_membro(membro_id: int, db: Session = Depends(get_db)):
    membro = db.query(models.Membro).filter(models.Membro.id == membro_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return membro


# ==== Atualiza dados de membros via /docs===#
@app.put("/membros/{membro_id}", response_model=schemas.MembroResponse)
def atualizar_membro(
    membro_id: int, dados: schemas.MembroCreate, db: Session = Depends(get_db)
):
    membro = db.query(models.Membro).filter(models.Membro.id == membro_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    for campo, valor in dados.model_dump().items():
        setattr(membro, campo, valor)

    db.commit()
    db.refresh(membro)
    return membro


# ==== Edita cadastro via formulario ====#
@app.get("/membros/{membro_id}/editar", response_class=None)
def form_editar(membro_id: int, request: Request, db: Session = Depends(get_db)):
    membro = db.query(models.Membro).filter(models.Membro.id == membro_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return templates.TemplateResponse(request, "editar.html", {"membro": membro})


@app.post("/membros/{membro_id}/editar")
def editar_via_formulario(
    membro_id: int,
    nome: str = Form(...),
    contato: Optional[str] = Form(None),
    data_nascimento: Optional[date] = Form(None),
    funcao: Optional[str] = Form(None),
    status: str = Form("ativo"),
    db: Session = Depends(get_db),
):
    membro = db.query(models.Membro).filter(models.Membro.id == membro_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    membro.nome = nome
    membro.contato = contato
    membro.data_nascimento = data_nascimento
    membro.funcao = funcao
    membro.status = status

    db.commit()
    return RedirectResponse(url="/membros/visualizar", status_code=303)


@app.post("/membros/{membro_id}/excluir")
def excluir_via_formulario(membro_id: int, db: Session = Depends(get_db)):
    membro = db.query(models.Membro).filter(models.Membro.id == membro_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    db.delete(membro)
    db.commit()
    return RedirectResponse(url="/membros/visualizar", status_code=303)


# ==== Deleta membro ===#


@app.delete("/membros/{membro_id}")
def excluir_membro(membro_id: int, db: Session = Depends(get_db)):
    membro = db.query(models.Membro).filter(models.Membro.id == membro_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    db.delete(membro)
    db.commit()
    return {"mensagem": f"Membro '{membro.nome}' excluido com sucesso!"}
