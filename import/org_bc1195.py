#!/usr/bin/python

import asm

"""
Import script for SPA des Cantons
28th October, 2016
15th April, 2016
"""

PATH = "data/bc1195_sample.csv"

def getdate(d):
    return asm.getdate_ddmmyy(d)

owners = []
ownerlicences = []
animals = []

ppo = {}

asm.setid("owner", 100)
asm.setid("ownerlicence", 100)
asm.setid("animal", 100)

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM ownerlicence WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"

# Load up data files
cfile = asm.csv_to_list(PATH, unicodehtml=True)

# Each row contains a person, animal and licence
for row in cfile:

    # person first
    personkey = row["Surname"] + row["Forename"] + row["Address #"]
    if ppo.has_key(personkey):
        o = ppo[personkey]
    else:
        o = asm.Owner()
        owners.append(o)
        ppo[personkey] = o
        o.OwnerForeNames = row["Forename"]
        o.OwnerSurname = row["Surname"]
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
        o.OwnerAddress = row["Address #"] + " " + row["Street Name"] + row["Street Type"]
        o.OwnerCounty = row["Town"]
        o.OwnerPostcode = row["Postcode"]
        o.HomeTelephone = row["Home Phone"]
        o.MobilePhone = row["Mobile Phone"]
        o.EmailAddress = row["Email"]

    # next the animal, assume that these are all unique and there's only one entry per animal
    # in this file.
    a = asm.Animal()
    animals.append(a)
    a.AnimalTypeID = 13 # Autre/Other
    a.SpeciesID = asm.species_from_db(row["Specie"])
    a.AnimalName = row["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateOfBirth = asm.getdate_yyyymmdd("1900/01/01")
    a.DateBroughtIn = a.DateOfBirth
    a.IsNonShelterAnimal = 1
    a.generateCode("A")
    a.BreedID = asm.breed_from_db(row["Breed"])
    a.Breed2ID = asm.breed_from_db(row["Crossbreed type"], 0)
    a.BreedName = row["Breed"]
    if row["Crossbreed type"] != "": a.BreedName += " / " + row["Crossbreed type"]
    a.BaseColourID = asm.colour_from_db(row["Colour"])
    a.IdentichipNumber = row["Microchipped Number"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.TattooNumber = row["Tattoo Number"]
    if a.TattooNumber != "": a.Tattoo = 1
    a.Neutered = asm.iif(row["Neutered/Spayed"] != "No", 1, 0)
    a.ShelterLocation = 1
    a.Markings = row["Marking"]
    a.Weight = asm.cint(row["Weight"])
    a.Sex = asm.getsex_mf(row["Sex"])
    a.Size = asm.size_from_db(row["Size"])
    a.CoatType = asm.coattype_from_db(row["Coat Type"])
    a.Archived = 1

    # the licence
    ol = asm.OwnerLicence()
    ownerlicences.append(ol)
    ol.OwnerID = o.ID
    ol.AnimalID = a.ID
    ol.LicenceTypeID = asm.licencetype_from_db(row["Licence Type"])
    ol.LicenceNumber = row["Licence Number"]
    ol.LicenceFee = asm.get_currency(row["Fee"])
    ol.IssueDate = asm.getdate_ddmmyyyy(row["Issued"])
    ol.ExpiryDate = asm.getdate_ddmmyyyy(row["Expired"])
    ol.Comments = row["Comments"]

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for ol in ownerlicences:
    print ol

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
