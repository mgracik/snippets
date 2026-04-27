class ViewGenerator:

    @staticmethod
    def build_select_clauses(source: DatabaseTable | DatabaseJsonColumn, fields: List[tuple[str, BlotterDatabaseField]]) -> List[str]:
        select_clauses = []
        for field_name, field_obj in fields:
            this = f"{source.alias}.{field_obj.name}" if not field_obj.custom_query else field_obj.name
            select_clauses.append(f"{field_obj.column_wrapper.format(this=this) if field_obj.column_wrapper else this} AS {field_name.upper()}")
        return select_clauses
    
    @staticmethod
    def build_from_clause(source: DatabaseTable | DatabaseJsonColumn, fields: List[tuple[str, BlotterDatabaseField]]) -> str:
        if isinstance(source, DatabaseTable):
            from_clause = f"LEFT JOIN {source.name} {source.alias} ON {source.join_condition}" if source.join_condition else f"{source.name} {source.alias}"
            return from_clause
        elif isinstance(source, DatabaseJsonColumn):
            columns = [f"{field.name} {field.return_type if field.return_type else 'VARCHAR2'} {'FORMAT JSON ' if not field.scalar else ''}PATH '$.{field.json_path}'" for _, field in fields]
            from_clause = f"OUTER APPLY JSON_TABLE({source.name}, '{source.json_path}'\n                 COLUMNS ({', '.join(columns)}) {source.alias}"
            return from_clause
        else:
            raise TypeError(f"Invalid source type: {type(source)}")

    def build_view_sql(self, view_name: str, select_clauses: List[str], from_clauses: List[str]) -> str:
        select_clause = ",\n               ".join(select_clauses)
        from_clause = "\n               ".join(from_clauses)
        
        return textwrap.dedent(f"""
        CREATE OR REPLACE VIEW {view_name} AS
        SELECT {select_clause}
          FROM {from_clause}
         WHERE LOWER(REQ.REQUEST_TYPE) = 'price';
        """)


    def create_view(self, blotter_fields: BlotterFields) -> str:
        select_clauses, from_clauses = [], []
        parsed_sources = set()

        for field_obj in dataclasses.fields(blotter_fields):
            field_name = field_obj.name
            blotter_field = field_obj.metadata["field"]
            if isinstance(blotter_field, BlotterDatabaseField):
                # SELECT clause.
                if isinstance(blotter_field.source, DatabaseTable):
                    this = f"{blotter_field.source.alias}.{blotter_field.name}" if not blotter_field.custom_query else blotter_field.name
                    select_clauses.append(f"{blotter_field.column_wrapper.format(this=this) if blotter_field.column_wrapper else this} AS {field_name.upper()}")
                elif isinstance(blotter_field.source, DatabaseJsonColumn):
                    json_func = "JSON_VALUE" if blotter_field.scalar else "JSON_QUERY"
                    returning = f" RETURNING {blotter_field.return_type}" if blotter_field.return_type else ""
                    select_clause = f"{json_func}({blotter_field.source.name}, '{blotter_field.source.json_path}.{blotter_field.json_path}'{returning}) AS {field_name.upper()}"
                    select_clauses.append(select_clause)

                # FROM clause.
                if isinstance(blotter_field.source, DatabaseTable):
                    source = blotter_field.source
                    if source not in parsed_sources:
                        from_clauses.append(f"LEFT JOIN {source.name} {source.alias} ON {source.join_condition}" if source.join_condition else f"{source.name} {source.alias}")
                        parsed_sources.add(source)

        return self.build_view_sql("VW_XXX", select_clauses, from_clauses)
        

    def create_view_bulk(self, blotter_fields: BlotterFields) -> str:
        sources = defaultdict(list)
        for field_obj in dataclasses.fields(blotter_fields):
            field_name = field_obj.name
            blotter_field = field_obj.metadata["field"]
            if isinstance(blotter_field, BlotterDatabaseField):
                sources[blotter_field.source].append((field_name, blotter_field))

        select_clauses, from_clauses = [], []
        for source, fieldlist in sources.items():
            select_clauses.extend(self.build_select_clauses(source, fieldlist))
            from_clauses.append(self.build_from_clause(source, fieldlist))
            
        return self.build_view_sql("VW_XXX_BULK", select_clauses, from_clauses)
