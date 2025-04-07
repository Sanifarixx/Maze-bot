from datetime import datetime
import re

async def is_date_in_range(date_to_check: str, start_date: str, end_date: str) -> bool:
  try:
    date_to_check = datetime.strptime(date_to_check, "%d.%m.%Y").date()
    start_date = datetime.strptime(start_date, "%d.%m.%Y").date()
    end_date = datetime.strptime(end_date, "%d.%m.%Y").date()
  except ValueError:
    return False

  return start_date <= date_to_check <= end_date

async def is_valid_date(date_str: str) -> bool:
  pattern  =  r"^\d{2}\.\d{2}\.\d{4}$"
  match = re.match(pattern, date_str)
  return bool(match)

async def check_nickname_format(nickname: str) -> bool:
    parts = nickname.split('_')
    if len(parts) !=2:
        return False
    if not parts[0] or not parts[1]:
        return False
    return True

async def check_punish_duration_format(input_string: str) -> bool:
    pattern = r"^(\d+)(s|m|h|d|w)$"
    match = re.match(pattern, input_string)
    
    if match:
        duration_value = int(match.group(1))
        if duration_value > 2000:
            return False
        return True
    return False