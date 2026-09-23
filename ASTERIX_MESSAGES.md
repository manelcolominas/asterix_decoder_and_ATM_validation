# ASTERIX CAT021 — Estructura a nivell de bit

Font: EUROCONTROL-SPEC-0149-12 *Surveillance Data Exchange — Part 12: ADS-B Reports* (Edition 2.1) i *ADS-B Target Reports — Reserved Expansion Field* (Edition 1.5).

Aquest document detalla, octet a octet i bit a bit, l'estructura dels Data Items utilitzats a `ASTERIX_MESSAGES.md`.

---

## 1. Estructura general del missatge

```
 -------------------------------------
|   CAT   |   LEN   |   DATA RECORD   |
 -------------------------------------
```

- **CAT** — 1 octet. Categoria ASTERIX (ex: `021` = ADS-B Target Reports).
- **LEN** — 2 octets. Longitud total del bloc en octets (CAT + LEN + Data Record).
- **DATA RECORD** — `FSPEC` + Data Fields.

---

## 2. FSPEC (Field Specification)

El FSPEC indica, bit a bit, quins Data Fields són presents al registre. Cada bit `Fn` correspon a un FRN (Field Reference Number). El bit `FX` (Field Extension) indica si hi ha un octet més de FSPEC.

**Convenció de numeració (ASTERIX §5):** en un FSPEC d'1 octet, els bits es numeren d'esquerra a dreta de l'1 al 8. En un FSPEC de p octets, es numeren d'esquerra a dreta de l'1 al p×8.

### FSPEC d'un sol octet

```
OCTET 1
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ F1 │ F2 │ F3 │ F4 │ F5 │ F6 │ F7 │ FX │
└────┴────┴────┴────┴────┴────┴────┴────┘
                                      │
                                      └── 1 → hi ha un altre octet
                                      └── 0 → fi del FSPEC
```

### FSPEC de dos (o més) octets

```
OCTET 1
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ F1 │ F2 │ F3 │ F4 │ F5 │ F6 │ F7 │ FX │
└────┴────┴────┴────┴────┴────┴────┴────┘
                                      │
                                      └── 1 → hi ha un altre octet

OCTET 2
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ F8 │ F9 │F10 │F11 │F12 │F13 │F14 │ FX │
└────┴────┴────┴────┴────┴────┴────┴────┘
                                      │
                                      └── 1 → hi ha un altre octet

OCTET 3
┌────┬────┬────┬────┬────┬────┬────┬────┐
│F15 │F16 │F17 │F18 │F19 │F20 │F21 │ FX │
└────┴────┴────┴────┴────┴────┴────┴────┘
                                      │
                                      └── 0 → fi del FSPEC
```

Cada `Fn` a 1 activa la presència, al Data Record, del Data Field associat a aquell FRN, seguint l'ordre creixent de FRN.

---

## 3. Data Items de CAT021

Convenció general (§5, Conventions): en un camp d'1 octet els bits es numeren d'1 a 8, de dreta a esquerra. En un camp de n octets (n>1), els octets es numeren d'esquerra a dreta de l'1 a n, i els bits de dreta a esquerra de l'1 a n×8. Els valors negatius es representen en complement a 2.

---

### I021/010 — Data Source Identification

**Format:** 2 octets, longitud fixa.

```
OCTET 1                                    OCTET 2
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b16│ b15│ b14│ b13│ b12│ b11│ b10│ b9 │ │ b8 │ b7 │ b6 │ b5 │ b4 │ b3 │ b2 │ b1 │
├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│                  SAC                  │ │                  SIC                  │
└───────────────────────────────────────┘ └───────────────────────────────────────┘
```

| Bits | Camp | Descripció |
|---|---|---|
| 16–9 | **SAC** | System Area Code |
| 8–1  | **SIC** | System Identification Code |

Present sempre en tot registre ASTERIX.

*Exemple (`ASTERIX_MESSAGES.md`): SAC = 0x02, SIC = 0x15.*

---

### I021/040 — Target Report Descriptor

**Format:** Longitud variable — subcamp primari d'1 octet + extensions d'1 octet cadascuna, activades pel bit `FX`.

#### Subcamp primari

```
OCTET 1
┌─────────────┬─────────┬────┬─────┬────┐
│     ATP     │   ARC   │ RC │ RAB │ FX │
├─────────────┼─────────┼────┼─────┼────┤
│    8  7  6  │  5    4 │ 3  │  2  │ 1  │
└─────────────┴─────────┴────┴─────┴────┘
```

| Bits | Camp | Valors |
|---|---|---|
| 8–6 | **ATP** Address Type | 0=ICAO 24-bit, 1=Duplicate address, 2=Surface vehicle, 3=Anonymous, 4-7=Reservat |
| 5–4 | **ARC** Altitude Reporting Capability | 0=25 ft, 1=100 ft, 2=Unknown, 3=Invalid |
| 3   | **RC** Range Check | 0=Default, 1=Range Check passat, CPR pendent |
| 2   | **RAB** Report Type | 0=Report del transponedor, 1=Report d'un field monitor |
| 1   | **FX** Field Extension | 0=Fi de l'item, 1=Hi ha 1a extensió |

#### 1a extensió

```
OCTET 1 (ext. 1)
┌────┬────┬────┬────┬────┬────┬────┬────┐
│DCR │GBS │SIM │TST │SAA │  CL     │ FX │
├────┼────┼────┼────┼────┼────┴────┼────┤
│ 8  │ 7  │ 6  │ 5  │ 4  │ 3     2 │ 1  │
└────┴────┴────┴────┴────┴─────────┴────┘
```

| Bit(s) | Camp | Valors |
|---|---|---|
| 8 | **DCR** Differential Correction | 0=Sense correcció, 1=Amb correcció diferencial (ADS-B) |
| 7 | **GBS** Ground Bit Setting | 0=No activat, 1=Activat |
| 6 | **SIM** Simulated Target | 0=Blanc real, 1=Blanc simulat |
| 5 | **TST** Test Target | 0=Default, 1=Blanc de prova |
| 4 | **SAA** Selected Altitude Available | 0=Capaç de proporcionar-la, 1=No capaç |
| 3–2 | **CL** Confidence Level | 0=Vàlid, 1=Sospitós, 2=Sense informació, 3=Reservat |
| 1 | **FX** Field Extension | 0=Fi de l'item, 1=Hi ha 2a extensió |

#### 2a extensió — Error Conditions

```
OCTET 1 (ext. 2)
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ 0  │ 0  │IPC │NOGO│ CPR│LDPJ│RCF │ FX │
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 8  │ 7  │ 6  │ 5  │ 4  │ 3  │ 2  │ 1  │
└────┴────┴────┴────┴────┴────┴────┴────┘
```

| Bit | Camp | Valors |
|---|---|---|
| 8–7 | (spare) | Fixat a 0 |
| 6 | **IPC** Independent Position Check | 0=Default, 1=Ha fallat |
| 5 | **NOGO** No-go Bit Status | 0=No activat, 1=Activat |
| 4 | **CPR** Compact Position Reporting | 0=Validació correcta, 1=Validació fallida |
| 3 | **LDPJ** Local Decoding Position Jump | 0=No detectat, 1=Detectat |
| 2 | **RCF** Range Check | 0=Default, 1=Ha fallat |
| 1 | **FX** Field Extension | 0=Fi de l'item, 1=Hi ha 3a extensió |

Aquest item és sempre present; les extensions només s'envien si algun bit és 1.

*Exemple (`ASTERIX_MESSAGES.md`): TYP = ADS-B ES Surface Position, SIM = No, RAB = No.*

---

### I021/070 — Mode 3/A Code in Octal Representation

**Format:** 2 octets, longitud fixa. Opcional.

```
OCTET 1                                    OCTET 2
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b16│ b15│ b14│ b13│ b12│ b11│ b10│ b9 │ │ b8 │ b7 │ b6 │ b5 │ b4 │ b3 │ b2 │ b1 │
├────┴────┴────┴────┼────┼────┼────┼────┤ ├────┼────┼────┼────┼────┼────┼────┼────┤
│   (spare) = 0     │ A4 │ A2 │ A1 │ B4 │ │ B2 │ B1 │ C4 │ C2 │ C1 │ D4 │ D2 │ D1 │
└───────────────────────────────────────┘ └───────────────────────────────────────┘
```

| Bits | Camp | Descripció |
|---|---|---|
| 16–13 | (spare) | Fixats a 0 |
| 12–1 | **A4 A2 A1 B4 B2 B1 C4 C2 C1 D4 D2 D1** | Codi Mode-3/A en representació octal |

*Exemple (`ASTERIX_MESSAGES.md`): Mode 3/A = 0456.*

---

### I021/073 — Time of Message Reception for Position

**Format:** 3 octets, longitud fixa. Opcional. Temps transcorregut des de la mitjanit anterior, en UTC.

```
OCTET 1                                     OCTET 2                                    OCTET 3
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b24│ b23│ b22│ b21│ b20│ b19│ b18│ b17│ │ b16│ b15│ b14│ b13│ b12│ b11│ b10│ b9 │ │ b8 │ b7 │ b6 │ b5 │ b4 │ b3 │ b2 │ b1 │
├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│                                         Time of Message Reception of Position (LSB = 2⁻⁷ s = 1/128 s)                     │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

| Bits | Camp | Descripció |
|---|---|---|
| 24–1 | **Time of Message Reception of Position** | LSB = 2⁻⁷ s (1/128 s). Es posa a zero cada mitjanit. |

Ha d'anar acompanyat, com a mínim, per I021/071 o I021/073 en un report amb informació de posició.

*Exemple (`ASTERIX_MESSAGES.md`): Time = 12:33:51.750 UTC.*

---

### I021/080 — Target Address

**Format:** 3 octets, longitud fixa. Sempre present.

```
OCTET 1                                     OCTET 2                                    OCTET 3
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b24│ b23│ b22│ b21│ b20│ b19│ b18│ b17│ │ b16│ b15│ b14│ b13│ b12│ b11│ b10│ b9 │ │ b8 │ b7 │ b6 │ b5 │ b4 │ b3 │ b2 │ b1 │
├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│                                             Target Address — A23 … A0 (24 bits)                                           │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

| Bits | Camp | Descripció |
|---|---|---|
| 24–1 | **Target Address** | Adreça de 24 bits (identificador de l'emissor), A23 a A0 |

*Exemple (`ASTERIX_MESSAGES.md`): Target Address = 0x4CA123.*

---

### I021/131 — High-Resolution Position in WGS-84 Co-ordinates

**Format:** 8 octets, longitud fixa. Opcional (alternativa a I021/130).

```
OCTET 1                                     OCTET 2
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b64│ b63│ b62│ b61│ b60│ b59│ b58│ b57│ │ b56│ b55│ b54│ b53│ b52│ b51│ b50│ b49│
├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│                         Latitude in WGS-84 (bits 64–33)                         │
└───────────────────────────────────────┴─────────────────────────────────────────┘

OCTET 3                                     OCTET 4
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b48│ b47│ b46│ b45│ b44│ b43│ b42│ b41│ │ b40│ b39│ b38│ b37│ b36│ b35│ b34│ b33│
├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│                         Latitude in WGS-84 (continuació) — LSB                  │
└───────────────────────────────────────┴─────────────────────────────────────────┘

OCTET 5                                     OCTET 6
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b32│ b31│ b30│ b29│ b28│ b27│ b26│ b25│ │ b24│ b23│ b22│ b21│ b20│ b19│ b18│ b17│
├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│                           Longitude in WGS-84 (bits 32–17)                      │
└───────────────────────────────────────┴─────────────────────────────────────────┘

OCTET 7                                     OCTET 8
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b16│ b15│ b14│ b13│ b12│ b11│ b10│ b9 │ │ b8 │ b7 │ b6 │ b5 │ b4 │ b3 │ b2 │ b1 │
├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│                      Longitude in WGS-84 (continuació) — LSB                    │
└───────────────────────────────────────┴─────────────────────────────────────────┘
```

| Bits | Camp | Descripció |
|---|---|---|
| 64–33 | **Latitude** | Complement a 2. Rang: -90° a 90°. LSB = 180/2³⁰ ° ≈ 1,6764×10⁻⁷ ° (≈2 cm de resolució) |
| 32–1 | **Longitude** | Complement a 2. Rang: -180° a <180°. LSB = 180/2³⁰ ° ≈ 1,6764×10⁻⁷ ° (≈2 cm de resolució) |

*Exemple (`ASTERIX_MESSAGES.md`): Latitude = 41.387400°, Longitude = 2.168600°.*

---

### I021/145 — Flight Level

**Format:** 2 octets, longitud fixa. Opcional. Nivell de vol barométric (no corregit amb QNH), en complement a 2.

```
OCTET 1                                    OCTET 2
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b16│ b15│ b14│ b13│ b12│ b11│ b10│ b9 │ │ b8 │ b7 │ b6 │ b5 │ b4 │ b3 │ b2 │ b1 │
├────┴────┴────┴────┴────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│                     Flight Level (complement a 2) — LSB                         │
└─────────────────────────────────────────┴───────────────────────────────────────┘
```

| Bits | Camp | Descripció |
|---|---|---|
| 16–1 | **Flight Level** | LSB = 1/4 FL. Rang: -15 FL ≤ FL ≤ 1500 FL |

*Exemple (`ASTERIX_MESSAGES.md`): Flight Level = FL350.*

---

### I021/170 — Target Identification

**Format:** 6 octets, longitud fixa. Opcional. 8 caràcters codificats en 6 bits cadascun (IA5 restringit, Doc 9871 / ICAO Annex 10 taula 3-9).

```
OCTET 1 (b48..b41)   OCTET 2 (b40..b33)   OCTET 3 (b32..b25)
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Char 1  │ Char 2..│ │..2 │ Char 3     │ │  Char 4  │ Char 5.│
└──────────────────┘ └──────────────────┘ └──────────────────┘

OCTET 4 (b24..b17)   OCTET 5 (b16..b9)    OCTET 6 (b8..b1)
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│..5 │ Char 6      │ │ Char 7  │ Char 8..│ │..8              │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

> Nota: com que 8 caràcters × 6 bits = 48 bits, els límits de caràcter (6 bits) no coincideixen amb els límits d'octet (8 bits); alguns caràcters queden partits entre dos octets consecutius (p. ex. Character 2 entre octet 1 i 2, Character 5 entre octet 3 i 4, Character 8 entre octet 5 i 6). La taula de bits següent és la referència exacta.

| Bits | Camp |
|---|---|
| 48–43 | Character 1 |
| 42–37 | Character 2 |
| 36–31 | Character 3 |
| 30–25 | Character 4 |
| 24–19 | Character 5 |
| 18–13 | Character 6 |
| 12–7  | Character 7 |
| 6–1   | Character 8 |

*Exemple (`ASTERIX_MESSAGES.md`): Target Identification = IBE1234.*

---

## 4. I021/REF — Reserved Expansion Field

**Format:** Camp compost. Subcamp primari d'1 octet (extensible amb FX) que indica quins subcamps opcionals segueixen.

### Subcamp primari

```
OCTET 1
┌────┬────┬────┬────┬────┬────┬────┬────┐
│BPS │SelH│ NAV│ GAO│ SGV│ STA│ TNH│ MES│
└────┴────┴────┴────┴────┴────┴────┴────┘
  8    7    6    5    4    3    2    1
```

| Bit | Camp | Valor 0 | Valor 1 |
|---|---|---|---|
| 8 | **BPS** | Barometric Pressure Setting absent | present |
| 7 | **SelH** | Selected Heading absent | present |
| 6 | **NAV** | Navigation Mode absent | present |
| 5 | **GAO** | GPS Antenna Offset absent | present |
| 4 | **SGV** | Surface Ground Vector absent | present |
| 3 | **STA** | Aircraft Status Information absent | present |
| 2 | **TNH** | True North Heading absent | present |
| 1 | **MES** | Military Extended Squitters absent | present |

*Nota: aquesta primera capa no porta FX (no s'estén més enllà de 8 subcamps a l'edició 1.5).*

Els subcamps s'envien, quan estan presents, en l'ordre de dalt a baix (BPS → MES).

---

### 4.1. Barometric Pressure Setting 'BPS'

**Format:** 2 octets, longitud fixa. Opcional.

```
OCTET 1                                    OCTET 2
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b16│ b15│ b14│ b13│ b12│ b11│ b10│ b9 │ │ b8 │ b7 │ b6 │ b5 │ b4 │ b3 │ b2 │ b1 │
├────┴────┴────┴────┼────┴────┴────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│ (spare) = 0000    │                                 BPS — LSB = 0.1 hPa         │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

| Bits | Camp | Descripció |
|---|---|---|
| 16–13 | (spare) | Fixats a 0 |
| 12–1 | **BPS** | Ajust de pressió barométrica. LSB = 0,1 hPa. Rang: 0–409,5 hPa (valor = pressió seleccionada a l'aeronau − 800 hPa) |

*Exemple (`ASTERIX_MESSAGES.md`): BPS = 1013.25 hPa → valor codificat = (1013.25 − 800) / 0.1 = 2132,5 → 2132 (0x854).*

---

### 4.2. Selected Heading 'SelH'

**Format:** 2 octets, longitud fixa. Opcional.

```
OCTET 1                                    OCTET 2
┌────┬────┬────┬────┬────┬────┬────┬────┐ ┌────┬────┬────┬────┬────┬────┬────┬────┐
│ b16│ b15│ b14│ b13│ b12│ b11│ b10│ b9 │ │ b8 │ b7 │ b6 │ b5 │ b4 │ b3 │ b2 │ b1 │
├────┴────┴────┴────┼────┼────┼────┴────┤ ├────┴────┴────┴────┴────┴────┴────┴────┤
│  (spare) = 0000    │HRD │Stat│                   SelH — LSB = 0,703125°         │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

| Bits | Camp | Descripció |
|---|---|---|
| 16–13 | (spare) | Fixats a 0 |
| 12 | **HRD** | Horizontal Reference Direction: 0=Nord vertader, 1=Nord magnètic |
| 11 | **Stat** | Estat: 0=Dada no disponible/invàlida, 1=Dada disponible i vàlida |
| 10–1 | **SelH** | Rumb seleccionat. LSB = 0,703125° |

*Exemple (`ASTERIX_MESSAGES.md`): SelH = 270°.*

---

### 4.3. Navigation Mode 'NAV'

**Format:** 1 octet, longitud fixa. Opcional.

```
OCTET 1
┌────┬────┬────┬────┬─────┬─────┬────┬────┐
│ AP │ VN │ AH │ AM │MFM#EP│MFM#VAL│(spare)│
├────┼────┼────┼────┼─────┼─────┼────┴────┤
│ 8  │ 7  │ 6  │ 5  │  4  │  3  │  2   1  │
└────┴────┴────┴────┴─────┴─────┴─────────┘
```

| Bit | Camp | Descripció |
|---|---|---|
| 8 | **AP** | Pilot automàtic engegat (=1) |
| 7 | **VN** | VNAV actiu (Vertical Navigation) (=1) |
| 6 | **AH** | Altitude Hold engegat (=1) |
| 5 | **AM** | Approach Mode actiu (=1) |
| 4 | **MFM#EP** | Element Populated: 0=no poblat, 1=poblat |
| 3 | **MFM#VAL** | Value: 0=bits MCP/FCU no poblats, 1=poblats |
| 2–1 | (spare) | Fixats a 0 |

*Exemple (`ASTERIX_MESSAGES.md`): NAV = ... (subcamp presenti, contingut segons AP/VN/AH/AM/MFM).*

---

## 5. Resum — Missatge d'exemple de `ASTERIX_MESSAGES.md`

| Data Item | Octets | FRN típic (UAP CAT021) |
|---|---|---|
| I021/010 | 2 | 1 |
| I021/040 | 1 + extensions | 2 |
| I021/070 | 2 | — |
| I021/080 | 3 | — |
| I021/073 | 3 | — |
| I021/131 | 8 | — |
| I021/145 | 2 | — |
| I021/170 | 6 | — |
| I021/REF | variable (compost) | — |

> El FRN exacte de cada Data Item depèn de l'UAP (User Application Profile) vigent per a CAT021, definida a l'Annex/Part corresponent de l'especificació EUROCONTROL.