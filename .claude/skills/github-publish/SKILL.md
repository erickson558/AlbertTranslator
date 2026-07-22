---
name: github-publish
description: Publica commits, tags y releases de AlbertTranslator en GitHub usando la cuenta autenticada erickson558 (gh CLI). Usar cuando el usuario pida "subir a GitHub", "publicar cambios", "hacer push a main", "crear un release", o cualquier variante de sincronizar el repo local con github.com/erickson558/AlbertTranslator.
---

# Publicar en GitHub (cuenta erickson558)

Este repositorio se publica en `https://github.com/erickson558/AlbertTranslator`
(publico, licencia Apache-2.0) usando la cuenta de GitHub **erickson558**, ya
autenticada via `gh` CLI con scopes `gist, read:org, repo, workflow` sobre
HTTPS. No se necesita pedir credenciales ni tokens: se asume sesion activa.

## Verificacion previa (siempre, antes de tocar nada remoto)

```bash
gh auth status
git remote -v
```

Confirmar que:

- La cuenta activa en `gh auth status` es `erickson558`.
- `origin` apunta a `https://github.com/erickson558/AlbertTranslator.git`.

Si cualquiera de las dos no coincide, **detenerse y avisar** en vez de hacer
push a un destino inesperado.

## Antes de mover nada: estado del working tree

```bash
git status
git diff --stat
```

Revisar que no se vayan a subir archivos sensibles o generados: `.env`, `*.log`,
`build/`, `dist/`, `release-artifacts/`, el `.exe` compilado. El `.gitignore`
del proyecto ya los excluye; si `git status` muestra alguno de estos como
"untracked" listo para `git add -A`, no forzar su inclusion.

## Flujo estandar (fix/feature ya validado y versionado)

Este proyecto exige que la version este sincronizada ANTES del commit
relevante (ver skill `python-qa-release`, Fase 4). Con eso ya hecho:

```bash
# 1) Verificar que VERSION/README/CHANGELOG estan alineados
python scripts/version_sync.py check

# 2) Agregar solo los archivos relevantes (evitar "git add -A" a ciegas)
git add <archivos tocados>

# 3) Commit con Conventional Commits + version entre parentesis
git commit -m "fix: descripcion breve del cambio (Vx.x.x)"

# 4) Tag de la version (debe coincidir exactamente con VERSION)
git tag Vx.x.x

# 5) Push de la rama y del tag
git push origin main
git push origin Vx.x.x
```

Notas sobre este flujo en este repo en particular:

- **El tag lo puede crear tambien el workflow de release** (`release.yml`)
  automaticamente en cada push a `main` con una version nueva no publicada
  todavia como tag remoto. Si se hizo el `git tag`/`git push origin Vx.x.x` a
  mano y el workflow tambien intenta crearlo, fallara "el tag ya existe" — en
  ese caso, dejar que el workflow gestione el tag y omitir el paso 4/5 manual,
  o verificar con `git ls-remote --tags origin` antes de tagear a mano.
- Si `git push origin main` es rechazado por estar desactualizado respecto al
  remoto, hacer `git fetch origin` y `git rebase origin/main` (o pedir
  instrucciones si hay conflictos) — nunca `push --force` a `main` sin
  confirmacion explicita del usuario.

## Verificar que el release se publico

```bash
gh run list --workflow release.yml --limit 5
gh release list --repo erickson558/AlbertTranslator --limit 5
```

Si el workflow de release falla, revisar el log con:

```bash
gh run view --repo erickson558/AlbertTranslator --log-failed
```

## Reglas de seguridad

- Nunca usar `--force` / `--force-with-lease` en push a `main` sin que el
  usuario lo pida explicitamente para esa accion puntual.
- Nunca borrar tags o releases existentes sin confirmacion explicita.
- Nunca cambiar la visibilidad del repositorio (publico/privado) ni la
  licencia sin que el usuario lo pida explicitamente.
- Si `gh auth status` muestra una cuenta distinta de `erickson558`, detenerse
  y preguntar antes de continuar — puede ser una maquina compartida.
