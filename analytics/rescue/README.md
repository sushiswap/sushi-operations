# Rescue Scripts Explained & steps to reproduce

1. Grab csvs from block explorers for all ERC20 token transfers for the whitehat address on each network

2. Run `python main.py` to generate the output directory

3. Run `python generate_tree_inputs.py` to consolidate duplicate user token entries and then generate the inputs that the merkle tree generation script will use outputting to /data/pre-tree-inputs/

4. Run `python check_output.py` to confirm that totals on the whitehat address match with totals in the pre-tree-input files for each network

5. Run `python check_for_dupes.py` to check for dupes in the pre-tree-input files

6. Copy inputs and bring them to use with this script to generate the merkle tree / proofs: https://github.com/jiro-ono/sushi-funds-returner

7. Copy the trees output from script above, and paste them in the data/trees/ directory

8. Run `python check_tree.py` to check the tree totals against the /data/output/ files
