import { Field, InputType } from '@nestjs/graphql';

@InputType('DataInput')
export class DataInput {
	constructor(
		origin = '',
		translated = '',
		translator = '',
		verified = false,
	) {
		this.origin = origin;
		this.translated = translated;
		this.translator = translator;
		this.verified = verified;
	}

	@Field(() => String, {
		nullable: false,
		description: 'the origin of sentence',
	})
	origin: string;

	@Field(() => String, {
		nullable: false,
		description: 'the translated of sentence',
	})
	translated: string;

	@Field(() => String, {
		nullable: false,
		description: "the sentence's translator",
	})
	translator: string;

	@Field(() => Boolean, {
		defaultValue: false,
		description: 'confirm that data is verified by authorizer',
	})
	verified: boolean;
}
