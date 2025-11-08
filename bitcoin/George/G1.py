from bitcoinutils.setup import setup
from bitcoinutils.transactions import Sequence
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
from bitcoinutils.script import Script
from bitcoinutils.proxy import NodeProxy
from bitcoinrpc.authproxy import JSONRPCException
from bitcoinutils.keys import P2shAddress, PublicKey

#tasks:
# Create new Bitcoin Address (P2PKH)
# Call the node's getnewaddress method
# Returns the address Pub Key

#dhmiourgia mias P2SH me block locktime
def create_p2sh():

    # choose network
    setup('regtest')
    wallet = 'wallet1'
    # Initialize RPC 
    rpcuser = "George"
    rpcpassword = "George_Michoulis_82"
    rpc_con = NodeProxy(rpcuser, rpcpassword).get_proxy()

    #connect with wallet, to opoio einai sta regtest/wallets, tsekaroume an einai hdh syndedemeno
    try:
        rpc_con.loadwallet(wallet)
    except JSONRPCException:
        # wallet already loaded
        pass
    
    #dimiourgoume mia nea dieythinsh, yparxei dn yparxei apo prin gia sigouria
    new_addr = rpc_con.getnewaddress() # a JSON-RPC method
    print('Address from getnewaddress: ',new_addr)
    privk = rpc_con.dumpprivkey(new_addr) # pairnoume to private key
    print('Private key: ', privk)
    pubk=rpc_con.getaddressinfo(new_addr)['pubkey'] #kai telika pairnoume to pub_key, me to opoio tha doulepsoume to p2sh

    # get  P2PKH address (public key)
    p2pkh = PublicKey(pubk)

    lock_height = 82 #dialegoume posa blocks na kleidosoume sto melon gia na ektelesei to transaction, dialeksa to AEM mou

    current_height = rpc_con.getblockcount() #pio block height exoume
    
    if(lock_height < current_height):
        print('\n ---- This height (%d) is lower than current height (%d) ----- ' %(lock_height, current_height))
    else:
        print('Funds lock is set: %d, wait because current height is %d' %(lock_height,current_height))
    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, lock_height) #create seq for the redeem script
    
    redeem= Script([seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh.to_hash160(),  'OP_EQUALVERIFY', 'OP_CHECKSIG'])
    
    #create P2SH address from above redeem script
    p2sh = P2shAddress.from_script(redeem)
    
    rpc_con.importaddress(p2sh.to_string()) #insert P2SH address into wallet
    
    print('The created P2SH address: ',p2sh.to_string())
    
    return(lock_height, privk, p2sh.to_string())

if __name__ == "__main__":
    lock_block_height, priv_key, p2sh_addr = create_p2sh()