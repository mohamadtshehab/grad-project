from pydantic import BaseModel, Field
from typing import List
from typing import List, Optional

class NameList(BaseModel):
    """Use this schema to format the character list output."""
    names: List[str] = Field(description="قائمة باسماء الشخصيات الموجودة في النص")

class Profile(BaseModel):
    
    name: str = Field(description="اسم الشخصية كما هو مذكور في البروفايل المعطى؛ لا يتم تغييره")

<<<<<<< HEAD
    age: Optional[str] = Field(
        default=None,
        description="العمر التقديري أو الوصف الدال عليه إذا تغير أو أضيف، اتركه None إذا لم يرد جديد"
    )
=======
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    role: Optional[str] = Field(
        default=None,
        description="الدور الجديد فقط إذا تغير. استخدم أداة character_role_classifier للتحقق من التغيير قبل الدمج"
    )
    
    physical_characteristics: Optional[List[str]] = Field(
        default_factory=list,
        description="الصفات الجسدية الجديدة فقط. اترك القائمة فارغة [] إذا لا يوجد جديد"
    )
    personality: Optional[List[str]] = Field(
        default_factory=list,
        description="الصفات النفسية الجديدة فقط. اترك القائمة فارغة [] إذا لا يوجد جديد"
    )
    events: Optional[List[str]] = Field(
        default_factory=list,
        description="الأحداث الجديدة فقط، إذا لم يوجد جديد اترك القائمة فارغة []"
    )
    relations: Optional[List[str]] = Field(
        default_factory=list,
        description='العلاقات الجديدة فقط مع الشخصيات الأخرى بصيغة "اسم_الشخصية: نوع_العلاقة". اترك القائمة [] إذا لا يوجد جديد'
    )
    aliases: Optional[List[str]] = Field(
        default_factory=list,
        description="الأسماء أو الألقاب الجديدة فقط. اترك القائمة [] إذا لا يوجد جديد"
    )


class Character(BaseModel):
    id: str = Field(
        description="معرف فريد للشخصية؛ لا يتغير خلال التحديث"
    )
    profile: Profile = Field(
        description="بروفايل الشخصية المحدث"
    )

class CharacterList(BaseModel):
    """Use this schema to format the profile refresher output."""
    profiles: List[Profile] = Field(description="قائمة من البروفايلات المحدثة للشخصيات")

class Summary(BaseModel):
    """Use this schema to format the summary output."""
    summary: str = Field(description="ملخص النص")

class Book(BaseModel):
    """Use this schema to format the book name extraction output."""
    book_name: str = Field(description="اسم الكتاب المستخرج من محتوى الملف")
    confidence: str = Field(description="مستوى الثقة في استخراج اسم الكتاب (عالي، متوسط، منخفض)")
    reasoning: str = Field(description="التفسير المنطقي لاختيار اسم الكتاب")

class TextQualityAssessment(BaseModel):
    """Use this schema to format the text quality assessment output."""
    quality_score: float = Field(description="درجة جودة النص من 0 إلى 1 (1 = ممتاز، 0 = سيء جداً)")
    quality_level: str = Field(description="مستوى الجودة (ممتاز، جيد، متوسط، سيء، سيء جداً)")
    issues: List[str] = Field(description="قائمة بالمشاكل المكتشفة في النص")
    suggestions: List[str] = Field(description="قائمة بالاقتراحات لتحسين جودة النص")
    reasoning: str = Field(description="التفسير المنطقي لتقييم جودة النص")

class TextClassification(BaseModel):
    """Use this schema to format the text classification output."""
    is_literary: bool = Field(description="هل النص أدبي أم لا (true = أدبي، false = غير أدبي)")
    classification: str = Field(description="تصنيف النص (أدبي، علمي، إخباري، تقني، ديني، تاريخي، إلخ)")
    confidence: float = Field(description="مستوى الثقة في التصنيف من 0 إلى 1")
    reasoning: str = Field(description="التفسير المنطقي لتصنيف النص")
    literary_features: List[str] = Field(description="قائمة بالخصائص الأدبية الموجودة في النص (إذا كان أدبياً)")
    non_literary_features: List[str] = Field(description="قائمة بالخصائص غير الأدبية الموجودة في النص (إذا لم يكن أدبياً)")

class EmptyProfileValidation(BaseModel):
    """Use this schema to format the empty profile validation output."""
    has_empty_profiles: bool = Field(description="هل توجد بروفايلات فارغة")
    empty_profiles: List[str] = Field(description="قائمة بأسماء البروفايلات الفارغة")
    suggestions: List[str] = Field(description="اقتراحات لتحسين البروفايلات")
    profiles: List[Profile] = Field(description="قائمة من البروفايلات المحدثة للشخصيات")
    validation_score: float = Field(description="درجة جودة البروفايلات من 0 إلى 1")
