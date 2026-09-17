#!/bin/bash
# Download loop para Estabelecimentos faltantes da RF
URL="https://api.exemplo.com/dados.rfb.gov.br/CNPJ/dados_abertos_cnpj/2026-01"
DEST="/mnt/ssd120/receita_federal"
MISSING=(0 1 2 6 7 8 9)
LOG="/mnt/ssd120/download_rf_loop.log"

echo "=== Download RF Loop iniciado em $(date) ===" > "$LOG"
echo "Arquivos faltantes: ${MISSING[*]}" >> "$LOG"

while true; do
    ALL_DONE=true
    for i in "${MISSING[@]}"; do
        FILE="2026-01_Estabelecimentos${i}.zip"
        # Skip if already downloaded and >100MB
        if [ -f "$DEST/$FILE" ]; then
            SIZE=$(stat -c%s "$DEST/$FILE" 2>/dev/null || echo 0)
            if [ "$SIZE" -gt 100000000 ]; then
                echo "[$(date)] $FILE ja existe ($SIZE bytes) - OK" >> "$LOG"
                continue
            fi
        fi
        ALL_DONE=false
        echo "[$(date)] Baixando $FILE..." >> "$LOG"
        wget -q --timeout=30 --tries=3 -O "$DEST/$FILE" "$URL/$FILE" 2>> "$LOG"
        if [ $? -eq 0 ]; then
            SIZE=$(stat -c%s "$DEST/$FILE" 2>/dev/null || echo 0)
            echo "[$(date)] $FILE baixado com sucesso ($SIZE bytes)" >> "$LOG"
        else
            echo "[$(date)] ERRO ao baixar $FILE" >> "$LOG"
            rm -f "$DEST/$FILE"
        fi
        sleep 2
    done
    if [ "$ALL_DONE" = true ]; then
        echo "[$(date)] TODOS OS ARQUIVOS BAIXADOS!" >> "$LOG"
        break
    fi
    echo "[$(date)] Aguardando 60s para nova tentativa..." >> "$LOG"
    sleep 60
done
echo "=== Download RF Loop finalizado em $(date) ===" >> "$LOG"
