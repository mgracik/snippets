class XXXBlotterGenerator:

    def create_blotter_sql(self, blotter_fields: BlotterFields) -> str:
        blotter_column_list, meta_column_list = [], []
        blotter_indexes, meta_indexes = [], []

        # Find the PK.
        blotter_pk, meta_pk = [], []
        for field_obj in dataclasses.fields(blotter_fields):
            blotter_field = field_obj.metadata["field"]
            if EFieldFlag.PK in blotter_field.flags:
                blotter_pk.append(field_obj.name)
                if EFieldFlag.META in blotter_field.flags:
                    meta_pk.append(field_obj.name)

        if len(blotter_pk) > 1 or len(meta_pk) > 1:
            raise Exception(f"Multiple primary keys defined: {blotter_pk}, {meta_pk}")

        # Get the columns DDL.
        for field_obj in dataclasses.fields(blotter_fields):
            field_name = field_obj.name
            blotter_field = field_obj.metadata["field"]
            if blotter_field.persist:
                column_ddl = f"{field_name.upper()} {blotter_field.XXX_type if blotter_field.XXX_type else 'VARCHAR2(4000)'}{' NOT NULL' if EFieldFlag.NOT_NULL in blotter_field.flags else ''}"
                blotter_column_list.append(column_ddl)
                if EFieldFlag.INDEXED in blotter_field.flags:
                    blotter_indexes.append(f"CREATE INDEX XXX_BLOTTER_{field_name.upper()}_IDX ON XXX_BLOTTER ({field_name.upper()})")
                if EFieldFlag.META in blotter_field.flags:
                    meta_column_list.append(column_ddl)
                    if EFieldFlag.INDEXED in blotter_field.flags:
                        meta_indexes.append(f"CREATE INDEX XXX_BLOTTER_META_{field_name.upper()}_IDX ON XXX_BLOTTER_META ({field_name.upper()})")

        # Add the constraints.
        for pk in blotter_pk:
            blotter_column_list.append(f"CONSTRAINT XXX_BLOTTER_PK PRIMARY KEY ({pk.upper()})")

        for pk in meta_pk:
            meta_column_list.append(f"CONSTRAINT XXX_BLOTTER_META_PK PRIMARY KEY ({pk.upper()})")

        # Generate the SQL.
        blotter_columns = ",\n            ".join(blotter_column_list)
        blotter_indexes = ";\n        ".join(blotter_indexes)

        return textwrap.dedent(f"""
        CREATE TABLE XXX_OWNER.XXX_BLOTTER (
            {blotter_columns}
        );
        GRANT SELECT, INSERT, UPDATE, DELETE ON XXX_OWNER.XXX_BLOTTER TO XXX_SYS;

        {blotter_indexes};
        COMMIT;
        """)
