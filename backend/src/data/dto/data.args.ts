import { ArgsType, Field, InputType } from '@nestjs/graphql';
import { IsDataExisted } from '../IsDataExisted';

@ArgsType()
@InputType()
export class NewDataInput {
	constructor(
		origin: string,
		translated: string,
		translator: string,
		verified: boolean,
	) {
		this.origin = origin;
		this.translated = translated;
		this.translator = translator;
		this.value = this.getCombinedValue();
		this.verified = verified;
	}

	@Field()
	origin: string;

	@Field()
	translated: string;

	@Field()
	translator: string;

	@Field()
	@IsDataExisted({ message: 'This data is already existed' })
	value: string;

	getCombinedValue(): string {
		return `${this.origin} ${this.translated} ${this.translator}`;
	}

	@Field()
	verified: boolean;
}
