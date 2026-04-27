if __name__ == "__main__":
    blotter_fields = BlotterFields()

    # Get the dependencies.
    dependencies: Dict[str, Set[str]] = defaultdict(set)
    for field_obj in dataclasses.fields(blotter_fields):
        blotter_field = field_obj.metadata["field"]
        if isinstance(blotter_field.dependencies, list):
            dependency_list = blotter_field.dependencies
        elif isinstance(blotter_field.dependencies, dict):
            dependency_list = blotter_field.dependencies.values()
        # Check for missing dependencies.
        missing = set(field.name for field in dependency_list if not hasattr(blotter_fields, field.name))
        if missing:
            raise Exception(f"Missing dependencies for '{field_obj.name}': {missing}")
        # Update the dependencies.
        dependencies[field_obj.name].update([field.name for field in dependency_list])

    # Get the execution plan.
    execution_plan = list(toposort.toposort(dependencies))

    # Print the required views SQL.
    print(ViewGenerator().create_view(blotter_fields))
    print(ViewGenerator().create_view_bulk(blotter_fields))

    # Print the XXX Blotter SQL.
    print(XXXBlotterGenerator().create_blotter_sql(blotter_fields))

    # Sample row from DB.
    db_row = {
        "quote_id": "Q123",
        "response_id": "R456",
        "stp_id": None,
        "response_original_data_status": "VALID_JSON",
        "stp_quote_data_status": None,
        "response_modified_timestamp": datetime(2024, 6, 1, 12, 0, 0),
        "stp_modified_timestamp": None,
        "stp_job_modified_timestamp": None,
        "today": date(2024, 6, 1),
        "request_type": "Price",
        "isin": "US1234567890",
        "kite_id": "KITE123",
        "underlyings": ["Underlying1", "Underlying2"]
    }

    # Init fields.
    blotter_fields = BlotterFields(**db_row)
    print(dataclasses.asdict(blotter_fields))

    # Update fields according to the execution plan.
    for field_set in execution_plan:
        for field_name in field_set:
            field_obj = blotter_fields.__dataclass_fields__[field_name]
            blotter_field = field_obj.metadata["field"]

            # Get the parameters for the function.
            if isinstance(blotter_field, BlotterDatabaseField):
                params = [getattr(blotter_fields, field_name)]
                kw_params = {}
            elif isinstance(blotter_field, BlotterDerivedField):
                if isinstance(blotter_field.dependencies, list):
                    params = [getattr(blotter_fields, field.name) for field in blotter_field.dependencies]
                    kw_params = {}
                elif isinstance(blotter_field.dependencies, dict):
                    params = []
                    kw_params = {param: getattr(blotter_fields, field.name) for param, field in blotter_field.dependencies.items()}

            # TODO: Add the context.
            ctx = None
            val = blotter_field.func(ctx, *params, **kw_params)

            # Save the value.
            setattr(blotter_fields, field_name, val)

    print(dataclasses.asdict(blotter_fields))

    # Prune not persisted fields.
    data = dataclasses.asdict(blotter_fields)
    for field_obj in dataclasses.fields(blotter_fields):
        blotter_field = field_obj.metadata["field"]
        if not blotter_field.persist:
            del data[field_obj.name]

    print(data)
