Basant-me en l'estàndard EUROCONTROL CAT048 i en com heu definit `DataItemSubfield` (pos + content: list[Any]) a `models.py`, aquí tens què hauria de retornar cada funció:

### `cat048_decoder.py:33` — Data Source Identification
Camp **fixe de 2 octets**:
- Octet 1: SAC (System Area Code), 0–255
- Octet 2: SIC (System Identification Code), 0–255

Hauria de retornar `DataItemSubfield(pos=..., content=[SAC, SIC])`.

### `cat048_decoder.py:36` — Time of Day
Camp **fixe de 3 octets**: enter sense signe de 24 bits, LSB = 1/128 s, indica el temps transcorregut des de mitjanit (UTC).

Hauria de retornar `content=[temps_en_segons]` (float), calculat com `valor_enter * (1/128)`.

### `cat048_decoder.py:39` — Target Report Descriptor
Camp **extès (FX)**, primer octet obligatori i octets addicionals opcionals mentre el bit FX (bit 1, LSB) estigui a 1:
- Octet 1: `TYP` (bits 8-6), `SIM` (bit 5), `RDP` (bit 4), `SPI` (bit 3), `RAB` (bit 2), `FX` (bit 1)
- Octet 2 (si FX=1): `TST` (bit 8), `ERR` (bit 7), `XPP` (bit 6), `ME` (bit 5), `MI` (bit 4), `FOE/FRI` (bits 3-2), `FX` (bit 1)

Hauria de retornar una llista de subcamps decodificats per cada octet (p. ex. `content=[TYP, SIM, RDP, SPI, RAB, ...ERR, ME, MI, FOE_FRI...]`), gestionant l'extensió segons el bit FX.

### `cat048_decoder.py:42` — Measured Position in Polar Co-ordinates
Camp **fixe de 4 octets**:
- Octets 1-2: RHO (distància), enter sense signe, LSB = 1/256 NM
- Octets 3-4: THETA (azimut), enter sense signe, LSB = 360/65536 graus

Hauria de retornar `content=[rho_en_NM, theta_en_graus]`.

### `cat048_decoder.py:45` — Mode 3/A Code in Octal Representation
Camp **fixe de 2 octets**:
- Bit 16: V (validated: 0=valid, 1=doubtful)
- Bit 15: G (garbled)
- Bit 14: L (0=Mode 3/A obtingut d'aquest cop d'antena, 1=no obtingut)
- Bit 13: spare
- Bits 12-1: codi Mode 3/A en 4 grups de 3 bits (A4 A2 A1, B4 B2 B1, C4 C2 C1, D4 D2 D1), que junts formen un codi octal de 4 dígits (0000-7777)

Hauria de retornar `content=[V, G, L, codi_octal]` (p. ex. codi com a string "1234" o enter interpretat en octal).

### `cat048_decoder.py:48` — Flight Level in Binary Representation
Camp **fixe de 2 octets**:
- Bit 16: V (validated)
- Bit 15: G (garbled)
- Bits 14-1: Flight Level en complement a 2, LSB = 1/4 FL

Hauria de retornar `content=[V, G, flight_level]`, on `flight_level` és el valor amb signe dividit per 4.

---

En tots els casos, cada funció hauria de:
1. Extreure el(s) bit(s)/octet(s) rellevants de `data`.
2. Aplicar l'escalat (LSB) corresponent per obtenir valors amb unitats reals (segons, NM, graus, FL, etc.).
3. Empaquetar els valors decodificats dins `content` d'un `DataItemSubfield`, seguint el mateix patró que ja s'utilitza per a la resta d'ítems.