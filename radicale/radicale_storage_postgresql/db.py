

class ContactRow(Base):
    """A single vCard in a VADDRESSBOOK collection.

    Structured columns are parsed from the vCard on every PUT/upload.
    Multi-value fields (emails, phones, addresses, urls, categories) are
    stored as JSONB arrays so they can be queried with PostgreSQL's JSON
    operators:
        SELECT * FROM contacts WHERE emails @> '[{"value": "alice@acme.com"}]';
    """

    __tablename__ = "contacts"

    # -- Parsed vCard fields -----------------
    full_name = Column(Text, nullable=True)              # FN
    given_name = Column(String(256), nullable=True)      # N -> given
    family_name = Column(String(256), nullable=True)     # N -> family
    additional_name = Column(String(256), nullable=True) # N -> additional (middle name)
    name_prefix = Column(String(64), nullable=True)      # N -> prefix (Dr., Mr.)
    name_suffix = Column(String(64), nullable=True)      # N -> suffix (Jr., PhD)
    nickname = Column(String(256), nullable=True)        # NICKNAME
    emails = Column(JSONB, nullable=True)                # [{"value": "a@b.com", "type": "work"}, ...]
    phones = Column(JSONB, nullable=True)                # [{"value": "+1...", "type": "cell"}, ...]
    organization = Column(String(256), nullable=True)    # ORG (first value)
    photo_uri = Column(Text, nullable=True)              # PHOTO URL form (https://...)
    photo = Column(LargeBinary, nullable=True)           # PHOTO base64-decoded binary (BYTEA)
    photo_media_type = Column(String(64), nullable=True) # e.g. "image/jpeg", "image/png"
    # Denormalized search columns (auto-populated on upload)
    # Flat text fields for trigram GIN indexes. The API searches these with
    # similarity() / ILIKE / % instead of querying individual structured columns.
    search_name = Column(Text, nullable=True)            # full_name + given + family + nickname + org
    search_emails = Column(Text, nullable=True)          # space-separated email addresses
    search_phones = Column(Text, nullable=True)          # space-separated phone numbers

    __table_args__ = (
        Index("idx_contacts_search_name_trgm", "search_name", postgresql_using="gin", postgresql_ops={"search_name": "gin_trgm_ops"}),
    )
