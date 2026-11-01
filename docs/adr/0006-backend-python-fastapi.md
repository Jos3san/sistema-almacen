# ADR-0006: Backend en Python + FastAPI

- **Estado:** Aceptado
- **Fecha:** 2026-10-27

## Contexto
El desarrollador es principiante en programación y DevOps, tiene ~8 semanas para el MVP (ADR-0005) y su carrera apunta a Cloud/Platform/MLOps. El sistema corre en un servidor pequeño en la nube con varios servicios.

## Decisión
Backend en **Python 3.13 + FastAPI**, con SQLAlchemy 2 (ORM), Pydantic (validación), Alembic (migraciones), pytest + Testcontainers (tests), Ruff (lint y formato) y uv (dependencias y entornos virtuales). PDFs con WeasyPrint.

## Alternativas consideradas
- Java 21 + Spring Boot: ecosistema de microservicios muy maduro y muy usado en empresas grandes de Perú, pero curva de aprendizaje alta y 250–500 MB de RAM por servicio frente a 50–100 MB.

## Consecuencias
- Positivas: avance rápido; un solo lenguaje para el backend y los scripts de DevOps; OpenAPI automático; menor costo de servidor.
- Negativas: tipado opcional (se mitiga con type hints, Pydantic y Ruff); menos "build" que aprender en el pipeline que con Java.
- Revisar: un servicio periférico podría escribirse en otro lenguaje más adelante como ejercicio.
