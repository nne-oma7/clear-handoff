from pydantic import  BaseModel, Field, field_validator, model_validator


from contact import  clean_email, clean_phone, is_valid_email, is_valid_phone



class ComplaintInput(BaseModel):
    message: str = Field(min_length=1, max_length=20000)


class ComplaintSubmission(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    answers: dict[str, str] = Field(default_factory=dict)
    contact_name: str = Field(default="", max_length=200)
    contact_email: str = Field(default="", max_length=254)
    contact_phone: str = Field(default="", max_length=30)

    @field_validator("contact_name")
    @classmethod
    def tidy_name(cls, value):
        return value.strip()

    @field_validator("contact_email")
    @classmethod
    def check_email(cls, value):
        value = clean_email(value)
        if value and not is_valid_email(value):
            raise ValueError("Please enter a valid email address.")
        return value

    @field_validator("contact_phone")
    @classmethod
    def check_phone(cls, value):
        value = clean_phone(value)
        if value and not is_valid_phone(value):
            raise ValueError("Please enter a valid phone number.")
        return value

    @model_validator(mode="after")
    def need_a_way_to_reach_them(self):
        if not self.contact_email and not self.contact_phone:
            raise ValueError(
                "Please provide an email address or a phone number."
            )
        return self


class TrackRequest(BaseModel):
    reference: str = Field(min_length=1, max_length=30)
    contact: str = Field(min_length=1, max_length=254)


class StatusUpdate(BaseModel):
    status: str