from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import bitcoin

# Server and bot settings
SERVER_IP = 'your_grouphug_backend_here'
SERVER_PORT = 12345
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token_here'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me a Bitcoin transaction in raw format.')

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tx_raw = update.message.text
    is_valid, message = validate_transaction(tx_raw)
    if is_valid:
        message_to_send = f"add_tx {tx_raw}"
        server_response = await send_to_server(message_to_send)
        response_message = 'Transaction processed. Server response: ' + server_response if server_response else 'Server did not respond.'
        await update.message.reply_text(response_message)
    else:
        await update.message.reply_text('Transaction validation failed: ' + message)

async def send_to_server(message):
    try:
        reader, writer = await asyncio.open_connection(SERVER_IP, SERVER_PORT)
        writer.write(message.encode())
        await writer.drain()
        response = await reader.read(100)
        return response.decode()
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()

def validate_transaction(tx_raw):
    tx_raw = tx_raw.strip().replace(' ', '')
    if any(c not in "0123456789abcdefABCDEF" for c in tx_raw):
        return False, "Transaction data contains non-hexadecimal characters."
    
    tx = bitcoin.deserialize(tx_raw)
    if len(tx['ins']) != len(tx['outs']) or len(tx['ins']) > 5 or tx['locktime'] != 0:
        return False, "Transaction validation failed."

    for input in tx['ins']:
        if 'witness' not in input or len(input['witness']) != 2 or input['witness'][-1][-1] != 0x83:
            return False, "Transaction validation failed."

    return True, "Transaction is valid."

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction))
    application.run_polling()

if __name__ == '__main__':
    main()
