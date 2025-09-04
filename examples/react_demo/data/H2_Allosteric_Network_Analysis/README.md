**Task**
    You are given a PDB ID and two residue positions. Model the protein as a residue interaction network where each residue's C-alpha atom is a node. An edge exists between two nodes if the distance between their C-alpha atoms is less than 7 Angstroms. Find the shortest path in this network between the two specified residues. Return the length of this path (i.e., the number of edges) as an integer. If no path exists, return -1. Format: <answer>int</answer>.

    **Steps**
    1) Download and parse the PDB file.
2) Create an empty graph using the `networkx` library.
3) Extract a list of all C-alpha atoms from the structure.
4) Add each residue (represented by its C-alpha atom and identified by its residue number) as a node to the graph.
5) Iterate through all unique pairs of C-alpha atoms. If the distance between a pair is less than 7.0, add an edge in the graph between their corresponding residue nodes.
6) Use `networkx.shortest_path_length` to calculate the shortest path between the two specified residue nodes. Handle the case where no path exists.
7) Return the calculated path length.

    **Variant**
    We don't need to download the data, the data is already in variant_1 folder

    1A3N
