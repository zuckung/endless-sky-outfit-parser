import os
from pathlib import Path
import pandas as pd

################################################################################

def main():
    print(f'Starting...')
    paths = []
    raw_df = pd.DataFrame()

    # Check all subdirectories for outfits
    for root, dirs, files in os.walk('.'):
        for name in files:
            if (
                ('outfits.txt' in name and 'deprecated' not in name) or
                'human\engines.txt' in os.path.join(root, name) or
                'human\power.txt' in os.path.join(root, name) or
                'human\weapons.txt' in os.path.join(root, name)):
                paths.append(os.path.join(root, name))
    raw_df = pd.concat([file_parser(path) for path in paths], join='outer', ignore_index=True)

    # Set up dataframes and export to xlsx
    group = raw_df.groupby('category')
    dfs = [group.get_group(g) for g in group.groups]
    with pd.ExcelWriter('outfits.xlsx') as writer:
        for df in dfs:
            new_df = df.dropna(axis='columns', how='all')
            new_df.to_excel(writer, sheet_name=df['category'].iloc[0])
    print(f'Parsing complete.')

################################################################################

def file_parser(path_str):
    print(f'Current file: {path_str}')
    path = Path(path_str)
    raw_data = []
    data = []
    
    with path.open() as file:
        # Get raw strings from file
        raw_data = map(lambda line: line.strip(), file.readlines())
        it = iter(raw_data)
        
        while (line := next(it, None)) is not None:
            if line.startswith('#') or len(line) <= 0:
                # Exclude comments and empty lines
                True
            else:
                # Pass this line and iterator to function
                outfit = outfit_parser(line, it)
                if outfit is not None:
                    # Skip effects
                    data.append(outfit)

    return pd.DataFrame.from_dict(data)

################################################################################
    
def outfit_parser(line, it):
    data = dict()
    line = line.strip()
    st = ' "'

    # Skip effects
    if line.startswith('effect'):
        while (line := next(it, None)):
            if len(line) <= 0:
                break
        return

    # Handle first line
    key, value = tuple(line.split(' ', 1))
    key, value = key.strip(st), value.strip(st)
    data[key] = value
    
    while (line := next(it, None)) is not None:
        if len(line) <= 0:
            # Stop and return on empty line
            break
        elif (
            line.startswith('description') or
            line.startswith('weapon') or
            line.startswith('stream') or
            line.startswith('cluster') or
            line.startswith('safe')):
            # Skip useless attributes
            continue
        elif line.startswith('licenses'):
            # Skip licenses
            next(it, None)
            continue
        else:
            key = str()
            value = str()
            if line.startswith('"'):
                # Split string after second quotation mark
                index = line.find('"', line.find('"') + 1, -1) + 1
                key, value = line[0:index], line[index - len(line):]
            else:
                # Split string on space
                key, value = tuple(line.split(' ', 1))
            key, value = key.strip(st), value.strip(st)
            data[key] = value
    return data

################################################################################

if __name__ == '__main__':
    main()
