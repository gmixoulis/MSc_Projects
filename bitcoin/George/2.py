from bitcoinutils.setup import setup
from bitcoinutils.transactions import Sequence
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
from bitcoinutils.proxy import NodeProxy
from bitcoinutils.transactions import TxOutput, Locktime, Transaction, TxInput
from bitcoinutils.keys import PrivateKey,PublicKey
from bitcoinutils.script import Script
from decimal import Decimal
from bitcoinutils.utils import to_satoshis
from G1 import create_p2sh

# Setup the network
setup('regtest') 
#init rpc
rpcuser = "George"
rpcpassword = "George_Michoulis_82"
rpc_con = NodeProxy(rpcuser, rpcpassword).get_proxy()


'''
● accept a future time, expressed either in block height or in UNIX Epoch time, and a
private key (to recreate the redeem script as above and also use to unlock the
P2PKH part)
● accept a P2SH address to get the funds from (the one created by the first script)
● check if the P2SH address has any UTXOs to get funds from
● accept a P2PKH address to send the funds to
● calculate the appropriate fees with respect to the size of the transaction
● send all funds that the P2SH address received to the P2PKH address provided
● display the raw unsigned transaction
● sign the transaction
● display the raw signed transaction
● display the transaction id
● verify that the transaction is valid and will be accepted by the Bitcoin nodes
● if the transaction is valid, send it to the blockchain
'''
# new P2SH using part1
lock_block_height, priv_key, p2sh = create_p2sh()
#100 blocks sto sto p2sh, gt eimaste large 
rpc_con.generatetoaddress(100, p2sh)
# mine 100 blocks gia na ginei to bitcoin spendable
for _ in range(100):
    rpc_con.generatetoaddress(1, rpc_con.getnewaddress())
# parinoume ta unspent UTXOs gia to P2SH address
p2sh_unspent = rpc_con.listunspent(0, 99999999, [p2sh])
print('\n')

print('h prwth synallagh pou tha treksoume',p2sh_unspent[0])
# create absolute-block locking sequence  gia to transaction
seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, lock_block_height)

#dimiourgo transaction inputs gia ta UTXOs kai ypologizw to synolo twn unspent bitcoins, gia eykolia to ypologizw mono gia 1 transaction, alla me mia mikrh tropopoihsh ginetai kai gia oles tis synallages
#txs = []
#unspent = 0
#for utxo in p2sh_unspent:
#        txs.append(TxInput(utxo['txid'], utxo['vout'], sequence=seq.for_input_sequence()))
#        unspent += utxo['amount']
txin=TxInput(p2sh_unspent[0]['txid'], p2sh_unspent[0]['vout'] , sequence=seq.for_input_sequence())
unspent=p2sh_unspent[0]['amount']       


# get the public key of the receiving address for the funds to be sent to
addr=rpc_con.getnewaddress()
pub_key = rpc_con.getaddressinfo(addr)['pubkey']
pk = PublicKey(pub_key)

def calc_fee(inputs):
    # Calculate transaction's size
    size = inputs * 180 + 34 * 1 + 10 + inputs
    # total fees (bytes *  53130 current medium fee per kb)
    total_fee = (size/1024)*(53130/10e8) # in BTCs
    return total_fee
print('\n')

in_amount = float(unspent)
fee = calc_fee(in_amount)
out_amount = round(in_amount-fee, 8)
print("out ammount ###############",out_amount)
tx_out = TxOutput(to_satoshis(out_amount),pk.get_address().to_script_pub_key())

# Lock time (in blocks) to be used in transaction
iLock = Locktime(lock_block_height).for_transaction()

# Compose transaction (Raw Unsigned Transaction)
p2sh_out = Transaction([txin], [tx_out], iLock)

raw = p2sh_out.serialize()
print('\n')
print('Raw Unsigned Transaction: ', raw)

#Sign  transaction

# Create signature to unlock inputs
# xrhsimopoioume to idio script p eixame kai sto part 1
p2pkh_sk = PrivateKey(priv_key)
#P2PKH public key
p2pkh_pk = p2pkh_sk.get_public_key().to_hex()
#P2PKH address (public key)
p2pkh_addr = p2pkh_sk.get_public_key().get_address()
#redeem script
redeem = Script([seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
# kai epeita h ypografh p tha xrisimopoihsoume
sign = p2pkh_sk.sign_input(p2sh_out, 0, redeem)

# Gia na ksekleidwsoume to transaction xrhsimopoioyme to signature, dhladh to P2SH public key kai to  redeem script
txin.script_sig = Script([sign, p2pkh_pk, redeem.to_hex()])

st = p2sh_out.serialize()
print('\n')
print('raw Signed Transaction: %s' %st)
tid = p2sh_out.get_txid()
print('\n')
print('raw Signed Transaction ID: ', tid)


 # Telos prepei na epalitheysoume oti to transaction einai valid
verify_me = rpc_con.testmempoolaccept([st])
if verify_me[0]['allowed']:
        # if transaction is valid send it to the blockchain (epallhla mploks)
    print('Transaction is valid and now it will be broadcasted.')
    rpc_con.sendrawtransaction(st)
    print('Transaction is  part of blockchain! GOOD')
else:
    print('tx rejected because: ', verify_me[0]['reject-reason'])

