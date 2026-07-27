
def get_species(self, species_id):

    cursor = self.cursor()

    print("SEARCHING SPECIES:", species_id)

    cursor.execute("""
        SELECT *
        FROM species
    """)

    print("ALL SPECIES:")
    for row in cursor.fetchall():
        print(dict(row))

    cursor.execute("""
        SELECT *
        FROM species
        WHERE id = ?
    """, (species_id,))

    return cursor.fetchone()