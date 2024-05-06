from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import bitcoin
import asyncio
import socket

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me a Bitcoin transaction in raw format.')

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tx_raw = update.message.text
    is_valid, message = validate_transaction(tx_raw)
    if is_valid:
        # Form the message to send to the server
        message_to_send = f"add_tx {tx_raw}"
        # Send the transaction to the server
        server_response = await send_to_server(message_to_send)
        if server_response:
            await update.message.reply_text('Transaction processed. Server response: ' + server_response)
        else:
            await update.message.reply_text('Failed to communicate with server.')
    else:
        await update.message.reply_text('Transaction validation failed: ' + message)

async def send_to_server(message):
    host = '10.0.0.8'  # Replace with your server IP
    port = 9090  # Replace with your server TCP port
    reader, writer = None, None
    try:
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(message.encode())
        await writer.drain()
        response = await reader.read(100)
        print(f"Server response: {response.decode()}")
        return response.decode()
    except Exception as e:
        print(f"Failed to send to server: {e}")
        return None
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()

def validate_transaction(tx_raw):
    try:
        tx = bitcoin.deserialize(tx_raw)
        # Check for equal number of inputs and outputs
        if len(tx['ins']) != len(tx['outs']):
            return False, "The number of inputs does not match the number of outputs."
        # Check for maximum 5 inputs
        if len(tx['ins']) > 5:
            return False, "The transaction has more than 5 inputs."
        # Check locktime
        if tx['locktime'] != 0:
            return False, "The transaction's locktime must be 0."
        # Check each input for the correct SigHash type
        for input in tx['ins']:
            if 'witness' in input and input['witness']:
            
                if len(input['witness']) != 2:
                    # If len of witness is diff from 2 we know is a P2WSH and not a P2WPKH
                    return False, "Script is not a P2WPKH"

                # Assuming the SigHash type is the last byte of the last item in the witness
                last_byte = input['witness'][-1][-1]
                if last_byte != (0x83):  # Hex 0x83 stands for SigHashType.SINGLE | SigHashType.ANYONECANPAY
                    return False, "One or more inputs do not use the required SigHash type SINGLE | ANYONECANPAY."
            
            else:
                return False, "Witness data missing or invalid in one or more inputs."
        return True, "Transaction is valid."
    except Exception as e:
        return False, f"Error during transaction validation: {e}"

def main() -> None:
    application = Application.builder().token('TELEGRAM_BOT_TOKEN').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction))

    application.run_polling()

if __name__ == '__main__':
    main()
