#!/usr/bin/env bash
set -euo pipefail

# install.sh — cria symlinks de ~/.claude/ para dentro do repo dev-profiles
# Idempotente: pode rodar quantas vezes quiser.

REPO_DIR="$HOME/.claude/dev-profiles"
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/backups/pre-install-$(date +%Y%m%d-%H%M%S)"

# 1. Valida que o clone está no lugar esperado
if [[ "$(realpath "$PWD")" != "$REPO_DIR" ]]; then
  echo "ERRO: rode este script de dentro de $REPO_DIR"
  echo "  cd $REPO_DIR && ./install.sh"
  exit 1
fi

echo "Instalando claude-setup em $CLAUDE_DIR..."
echo ""

# 2. Backup do estado atual se os dirs existirem como dir normal (não symlink)
BACKUP_DONE=0
for dir in profiles skills agents; do
  target="$CLAUDE_DIR/$dir"
  if [[ -e "$target" && ! -L "$target" ]]; then
    if [[ "$BACKUP_DONE" == "0" ]]; then
      mkdir -p "$BACKUP_DIR"
      BACKUP_DONE=1
    fi
    mv "$target" "$BACKUP_DIR/"
    echo "  Backup: $target → $BACKUP_DIR/$dir"
  fi
done

# 3. Cria/atualiza symlinks
ln -sfn "$REPO_DIR/profiles" "$CLAUDE_DIR/profiles"
ln -sfn "$REPO_DIR/skills"   "$CLAUDE_DIR/skills"
ln -sfn "$REPO_DIR/agents"   "$CLAUDE_DIR/agents"

echo "  ✓ ~/.claude/profiles → dev-profiles/profiles"
echo "  ✓ ~/.claude/skills   → dev-profiles/skills"
echo "  ✓ ~/.claude/agents   → dev-profiles/agents"

# 4. Symlink do CLAUDE.md ativo (perfil default: esp32)
CURRENT_CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
if [[ ! -e "$CURRENT_CLAUDE_MD" ]] || [[ -L "$CURRENT_CLAUDE_MD" ]]; then
  # Se não existir ou já for symlink, relinka pro esp32 default
  # (se já for symlink pra um perfil específico, mantém)
  if [[ -L "$CURRENT_CLAUDE_MD" ]]; then
    existing_target=$(readlink "$CURRENT_CLAUDE_MD")
    # Se o symlink atual aponta pra um perfil conhecido, preserva
    case "$existing_target" in
      */profiles/*.md)
        profile_name=$(basename "$existing_target")
        ln -sfn "$REPO_DIR/profiles/$profile_name" "$CURRENT_CLAUDE_MD"
        echo "  ✓ CLAUDE.md → profiles/$profile_name (preservado)"
        ;;
      *)
        ln -sfn "$REPO_DIR/profiles/esp32.md" "$CURRENT_CLAUDE_MD"
        echo "  ✓ CLAUDE.md → profiles/esp32.md (default)"
        ;;
    esac
  else
    ln -sfn "$REPO_DIR/profiles/esp32.md" "$CURRENT_CLAUDE_MD"
    echo "  ✓ CLAUDE.md → profiles/esp32.md (default)"
  fi
else
  echo "  ! CLAUDE.md existe como arquivo — não foi tocado"
fi

# 5. Relatório final
echo ""
echo "✓ Instalação concluída"
echo ""
echo "Perfis disponíveis:"
for profile in "$REPO_DIR/profiles/"*.md; do
  name=$(basename "$profile" .md)
  echo "  - $name"
done
echo ""
echo "Perfil ativo (CLAUDE.md):"
if [[ -L "$CURRENT_CLAUDE_MD" ]]; then
  echo "  $(readlink "$CURRENT_CLAUDE_MD")"
fi
echo ""
echo "Para trocar o perfil ativo:"
echo "  ln -sfn $REPO_DIR/profiles/flutter.md $CLAUDE_DIR/CLAUDE.md"
echo "  ln -sfn $REPO_DIR/profiles/systems.md $CLAUDE_DIR/CLAUDE.md"
echo "  ln -sfn $REPO_DIR/profiles/frontend-web.md $CLAUDE_DIR/CLAUDE.md"

if [[ "$BACKUP_DONE" == "1" ]]; then
  echo ""
  echo "Backup do estado anterior em: $BACKUP_DIR"
fi
