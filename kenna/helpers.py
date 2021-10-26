def object_type_to_data_export_type(object_type: str) -> str:
    if object_type in ['asset', 'assets']:
        return 'asset'
    elif object_type in ['vulnerability', 'vulnerabilities']:
        return 'vulnerability'
    elif object_type in ['fix', 'fixes']:
        return 'fix'
    else:
        raise ValueError(object_type)
