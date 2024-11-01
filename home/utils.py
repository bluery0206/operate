def get_full_name(profile:object, m_initial:bool=True):
	full_name = profile.l_name

	if profile.f_name:
		full_name += f", {profile.f_name}"

	if profile.m_name:
		full_name += f" {profile.m_name}"
	elif profile.m_name and m_initial:
		full_name += f" {profile.m_name[0]}."

	if profile.suffix:
		full_name += f" {profile.suffix}"

	return full_name
