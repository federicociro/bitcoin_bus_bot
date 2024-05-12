from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
)
from dotenv import load_dotenv
import asyncio
import os
import bitcoin

load_dotenv()

async def handle_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
  -> None:
    await update.message.reply_text("Send me a Bitcoin transaction in raw format")

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tx_raw = update.message.text
    is_valid, message = validate_transaction(tx_raw)
    if is_valid:
        message_to_send = f"add_tx {tx_raw}"
        server_response = await send_to_server(message_to_send)
        await update.message.reply_text('Transaction processed. Server response: ' + server_response)
    else:
        await update.message.reply_text('Transaction validation failed: ' + message)

async def send_to_server(message):
    host = os.getenv('SERVER_IP')
    port = int(os.getenv('SERVER_PORT'))
    try:
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(message.encode())
        await writer.drain()
        response = await reader.read(100)
        return response.decode()
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()

def validate_transaction(tx_raw):
    # Strip and remove all spaces
    tx_raw = tx_raw.strip().replace(' ', '')

    # Check if all characters are valid hexadecimal
    if any(c not in "0123456789abcdefABCDEF" for c in tx_raw):
        return False, "Transaction data contains non-hexadecimal characters."

    # Deserialize the transaction
    try:
        tx = bitcoin.deserialize(tx_raw)
    except Exception as e:
        return False, f"Failed to deserialize transaction: {str(e)}"

    # Check the number of inputs and outputs
    if len(tx['ins']) != len(tx['outs']):
        return False, "The number of inputs does not match the number of outputs."

    # Check for maximum input limit
    if len(tx['ins']) > 5:
        return False, "The transaction has more than 5 inputs, which is not allowed."

    # Check the locktime of the transaction
    if tx['locktime'] != 0:
        return False, "The transaction's locktime must be 0. Found locktime: {}".format(tx['locktime'])

    # Check each input for the correct witness structure
    for index, input in enumerate(tx['ins']):
        if 'witness' not in input or len(input['witness']) != 2:
            return False, f"Input {index + 1} has an invalid witness structure. Required: 2 items in the witness."

        # Assuming the SigHash type is the last byte of the last item in the witness
        last_byte = input['witness'][-1][-1]
        if last_byte != 0x83:
            return False, f"Input {index + 1} does not use the required SigHash type SINGLE | ANYONECANPAY."

    # If all checks are passed
    return True, "Transaction is valid."

def main() -> None:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction))
    application.run_polling()

if __name__ == '__main__':
    main()