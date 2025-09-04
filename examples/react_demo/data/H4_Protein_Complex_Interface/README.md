**Task**
    For a given multi-chain PDB of a protein complex, analyze the interface between chains. You must count the total number of inter-chain contacts within a 4.5 Angstrom distance cutoff. An inter-chain contact is defined as a pair of residues, one from each of two different chains, that have at least one pair of atoms closer than the cutoff. Return the total count of unique interacting residue pairs. Format: <answer>int</answer>.

    **Steps**
    1) Download and parse the PDB file.
2) Get a list of all atoms in the structure.
3) Use `Bio.PDB.NeighborSearch` to find all atom pairs within the 4.5 Å cutoff.
4) Create a set to store unique interacting residue pairs.
5) Iterate through the atom pairs. For each pair, get their parent residues and chain IDs.
6) If the chain IDs are different, it's an inter-chain contact.
7) Add the pair of residue objects (in a sorted tuple to ensure uniqueness regardless of order) to the set.
8) The final answer is the size of this set. Return this count.

    **Variant**
    We don't need to download the data, the data is already in variant_1 folder

    4HHB
