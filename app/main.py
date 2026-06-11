import os
from fastapi import FastAPI, HTTPException, Depends  # type: ignore[import]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import]
from pydantic import BaseModel  # type: ignore[import]
from sqlalchemy import create_engine, Column, Integer, String  # type: ignore[import]
from sqlalchemy.orm import sessionmaker, Session, declarative_base  # type: ignore[import]

# ========================================
# 1. CONFIGURACIÓN DE LA BASE DE DATOS
# ========================================
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cursos.db")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ========================================
# 2. DISEÑO DE LA TABLA (SQLAlchemy)
# Al ponerlo aquí, ya no necesitamos importar nada
# ========================================
class CursoDB(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String)
    nivel = Column(String)
    fecha = Column(String)
    estado = Column(String)
    imagen = Column(String)

# ¡Línea mágica que crea la tabla físicamente si no existe!
Base.metadata.create_all(bind=engine)

# ========================================
# 3. INICIALIZACIÓN DE FASTAPI Y CORS
# ========================================
app = FastAPI(title="ChessAcademy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================================
# 4. MODELOS PYDANTIC (Validación de Frontend)
# ========================================
class CursoCreate(BaseModel):
    nombre: str
    descripcion: str
    nivel: str
    fecha: str
    estado: str
    imagen: str

class CursoResponse(CursoCreate):
    id: int
    class Config:
        from_attributes = True

# ========================================
# 5. ENDPOINTS (RUTAS API)
# ========================================
@app.get("/api/cursos", response_model=list[CursoResponse])
def obtener_cursos(db: Session = Depends(get_db)):
    return db.query(CursoDB).all()

@app.post("/api/cursos", response_model=CursoResponse)
def crear_curso(curso: CursoCreate, db: Session = Depends(get_db)):
    nuevo_curso = CursoDB(**curso.model_dump())
    db.add(nuevo_curso)
    db.commit()
    db.refresh(nuevo_curso)
    return nuevo_curso

@app.put("/api/cursos/{curso_id}", response_model=CursoResponse)
def actualizar_curso(curso_id: int, curso_actualizado: CursoCreate, db: Session = Depends(get_db)):
    curso_bd = db.query(CursoDB).filter(CursoDB.id == curso_id).first()
    if not curso_bd:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    for key, value in curso_actualizado.model_dump().items():
        setattr(curso_bd, key, value)
    
    db.commit()
    db.refresh(curso_bd)
    return curso_bd

@app.delete("/api/cursos/{curso_id}")
def eliminar_curso(curso_id: int, db: Session = Depends(get_db)):
    curso_bd = db.query(CursoDB).filter(CursoDB.id == curso_id).first()
    if not curso_bd:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    db.delete(curso_bd)
    db.commit()
    return {"mensaje": "Curso eliminado correctamente"}